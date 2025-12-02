import * as parser from '@babel/parser';
import traverse, { type NodePath } from '@babel/traverse';
import generate from '@babel/generator';
import * as t from '@babel/types';
import { logConfig } from './config';

interface InstrumentOptions {
  filePath: string;
  code: string;
}

function shouldInstrumentFile(filePath: string): boolean {
  const { include, exclude, filePatterns } = logConfig.patterns;

  if (exclude?.some((pattern) => pattern.test(filePath))) {
    return false;
  }

  if (include && !include.some((pattern) => pattern.test(filePath))) {
    return false;
  }

  if (filePatterns && !filePatterns.some((pattern) => pattern.test(filePath))) {
    return false;
  }

  return true;
}

function shouldInstrumentFunction(functionName: string): boolean {
  if (!functionName || functionName === 'anonymous') return false;

  const { functionPatterns } = logConfig.patterns;

  if (!functionPatterns || functionPatterns.length === 0) {
    return true;
  }

  return functionPatterns.some((pattern) => pattern.test(functionName));
}

function getModuleName(filePath: string): string {
  let name = filePath;

  if (name.includes('/qx-ui/src/')) {
    name = name.split('/qx-ui/src/')[1];
  } else if (name.includes('/qx-ts/src/')) {
    name = name.split('/qx-ts/src/')[1];
  } else if (name.includes('/src/')) {
    name = name.split('/src/')[1];
  } else {
    const parts = name.split('/');
    name = parts[parts.length - 1];
  }

  name = name.replace(/\.(ts|tsx|js|jsx)$/, '');

  if (name.startsWith('api/rw/')) {
    name = name.replace(/^api\/rw\//, '');
  }

  name = name.replace(/\//g, '.');

  return `qx.${name}`;
}

function createLoggerImport(): t.ImportDeclaration {
  const importPath = logConfig.project?.loggerImportPath || '/plugins/log-bot/logger';

  return t.importDeclaration(
    [t.importSpecifier(t.identifier('logbot'), t.identifier('logbot'))],
    t.stringLiteral(importPath),
  );
}

function createTimingVariable(functionName: string): t.VariableDeclaration {
  return t.variableDeclaration('const', [
    t.variableDeclarator(
      t.identifier(`__logStart_${functionName}`),
      t.callExpression(
        t.memberExpression(t.identifier('Date'), t.identifier('now')),
        [],
      ),
    ),
  ]);
}

function createEntryLog(
  moduleName: string,
  functionName: string,
  paramNames: string[],
): t.ExpressionStatement {
  const args: t.Expression[] = [
    t.stringLiteral(moduleName),
    t.stringLiteral(functionName),
  ];

  if (logConfig.capture.args && paramNames.length > 0) {
    args.push(
      t.arrayExpression(paramNames.map((name) => t.identifier(name))),
    );
  }

  return t.expressionStatement(
    t.callExpression(
      t.memberExpression(t.identifier('logbot'), t.identifier('entry')),
      args,
    ),
  );
}

function createExitLog(
  moduleName: string,
  functionName: string,
  resultIdentifier?: t.Identifier,
): t.ExpressionStatement {
  const args: t.Expression[] = [
    t.stringLiteral(moduleName),
    t.stringLiteral(functionName),
  ];

  if (logConfig.capture.return && resultIdentifier) {
    args.push(resultIdentifier);
  } else {
    args.push(t.identifier('undefined'));
  }

  if (logConfig.capture.timing) {
    args.push(
      t.binaryExpression(
        '-',
        t.callExpression(
          t.memberExpression(t.identifier('Date'), t.identifier('now')),
          [],
        ),
        t.identifier(`__logStart_${functionName}`),
      ),
    );
  }

  return t.expressionStatement(
    t.callExpression(
      t.memberExpression(t.identifier('logbot'), t.identifier('exit')),
      args,
    ),
  );
}

function createErrorLog(
  moduleName: string,
  functionName: string,
): t.ExpressionStatement {
  return t.expressionStatement(
    t.callExpression(
      t.memberExpression(t.identifier('logbot'), t.identifier('error')),
      [
        t.stringLiteral(moduleName),
        t.stringLiteral(functionName),
        t.identifier('__logError'),
      ],
    ),
  );
}

function wrapFunctionBody(
  path: NodePath<
    t.FunctionDeclaration | t.FunctionExpression | t.ArrowFunctionExpression | t.ObjectMethod
  >,
  moduleName: string,
  functionName: string,
): void {
  // Skip generator functions - instrumenting them breaks yield semantics
  if (path.node.generator) {
    console.warn(
      `[log-bot] Skipping generator function: ${moduleName}.${functionName} (generators not supported)`
    );
    return;
  }

  const params = path.node.params;
  const paramNames = params
    .filter((param: t.Node): param is t.Identifier => t.isIdentifier(param))
    .map((param: t.Identifier) => param.name);

  let body = path.node.body;

  if (!t.isBlockStatement(body)) {
    body = t.blockStatement([t.returnStatement(body as t.Expression)]);
    path.node.body = body;
  }

  const originalStatements = body.body;
  const isAsync = path.node.async;

  const timingVar = logConfig.capture.timing
    ? createTimingVariable(functionName)
    : null;
  const entryLog = createEntryLog(moduleName, functionName, paramNames);

  const instrumentedBody: t.Statement[] = [];

  if (timingVar) {
    instrumentedBody.push(timingVar);
  }
  instrumentedBody.push(entryLog);

  if (isAsync) {
    const instrumentedStatements: t.Statement[] = [];

    for (const statement of originalStatements) {
      if (t.isReturnStatement(statement)) {
        const returnValue = statement.argument;
        if (returnValue && logConfig.capture.return) {
          const resultId = t.identifier('__logResult');
          instrumentedStatements.push(
            t.variableDeclaration('const', [
              t.variableDeclarator(resultId, returnValue),
            ]),
          );
          instrumentedStatements.push(
            t.expressionStatement(
              t.awaitExpression(
                t.callExpression(
                  t.arrowFunctionExpression(
                    [],
                    t.blockStatement([
                      createExitLog(moduleName, functionName, resultId),
                      t.returnStatement(t.identifier('undefined')),
                    ]),
                  ),
                  [],
                ),
              ),
            ),
          );
          instrumentedStatements.push(t.returnStatement(resultId));
        } else {
          if (logConfig.capture.timing) {
            instrumentedStatements.push(
              createExitLog(moduleName, functionName),
            );
          }
          instrumentedStatements.push(statement);
        }
      } else {
        instrumentedStatements.push(statement);
      }
    }

    if (logConfig.capture.timing && !hasExplicitReturn(originalStatements)) {
      instrumentedStatements.push(createExitLog(moduleName, functionName));
    }

    instrumentedBody.push(
      t.tryStatement(
        t.blockStatement(instrumentedStatements),
        t.catchClause(
          t.identifier('__logError'),
          t.blockStatement([
            createErrorLog(moduleName, functionName),
            t.throwStatement(t.identifier('__logError')),
          ]),
        ),
      ),
    );
  } else {
    const instrumentedStatements: t.Statement[] = [];

    for (const statement of originalStatements) {
      if (t.isReturnStatement(statement)) {
        const returnValue = statement.argument;
        if (returnValue && logConfig.capture.return) {
          const resultId = t.identifier('__logResult');
          instrumentedStatements.push(
            t.variableDeclaration('const', [
              t.variableDeclarator(resultId, returnValue),
            ]),
          );
          instrumentedStatements.push(
            createExitLog(moduleName, functionName, resultId),
          );
          instrumentedStatements.push(t.returnStatement(resultId));
        } else {
          if (logConfig.capture.timing) {
            instrumentedStatements.push(
              createExitLog(moduleName, functionName),
            );
          }
          instrumentedStatements.push(statement);
        }
      } else {
        instrumentedStatements.push(statement);
      }
    }

    instrumentedBody.push(
      t.tryStatement(
        t.blockStatement(instrumentedStatements),
        t.catchClause(
          t.identifier('__logError'),
          t.blockStatement([
            createErrorLog(moduleName, functionName),
            t.throwStatement(t.identifier('__logError')),
          ]),
        ),
        logConfig.capture.timing && !hasExplicitReturn(originalStatements)
          ? t.blockStatement([createExitLog(moduleName, functionName)])
          : undefined,
      ),
    );
  }

  body.body = instrumentedBody;
}

function hasExplicitReturn(statements: t.Statement[]): boolean {
  return statements.some((stmt) => t.isReturnStatement(stmt));
}

export function instrumentCode({ filePath, code }: InstrumentOptions): {
  code: string;
  map: ReturnType<typeof generate>['map'];
} | null {
  if (!shouldInstrumentFile(filePath)) {
    return null;
  }

  if (!code.includes('function') && !code.includes('=>')) {
    return null;
  }

  let ast: t.File;
  try {
    ast = parser.parse(code, {
      sourceType: 'module',
      plugins: ['typescript', 'jsx'],
    });
  } catch (error) {
    console.error(`Failed to parse ${filePath}:`, error);
    return null;
  }

  const moduleName = getModuleName(filePath);
  let modified = false;

  try {
    traverse(ast, {
      FunctionDeclaration(path) {
        const functionName = path.node.id?.name;
        if (!functionName || !shouldInstrumentFunction(functionName)) return;

        wrapFunctionBody(path, moduleName, functionName);
        modified = true;
      },

      FunctionExpression(path) {
        const functionName =
          path.node.id?.name ||
          (path.parent &&
          t.isVariableDeclarator(path.parent) &&
          t.isIdentifier(path.parent.id)
            ? path.parent.id.name
            : 'anonymous');

        if (!shouldInstrumentFunction(functionName)) return;

        wrapFunctionBody(path, moduleName, functionName);
        modified = true;
      },

      ArrowFunctionExpression(path) {
        const parent = path.parent;
        let functionName = 'anonymous';

        if (t.isVariableDeclarator(parent) && t.isIdentifier(parent.id)) {
          functionName = parent.id.name;
        } else if (
          t.isObjectProperty(parent) &&
          t.isIdentifier(parent.key)
        ) {
          functionName = parent.key.name;
        } else if (t.isClassMethod(parent) && t.isIdentifier(parent.key)) {
          functionName = parent.key.name;
        }

        if (!shouldInstrumentFunction(functionName)) return;

        wrapFunctionBody(path, moduleName, functionName);
        modified = true;
      },

      ObjectMethod(path) {
        // Handle object method shorthand: { method() { } }
        const functionName = t.isIdentifier(path.node.key)
          ? path.node.key.name
          : 'anonymous';

        if (!shouldInstrumentFunction(functionName)) return;

        wrapFunctionBody(path, moduleName, functionName);
        modified = true;
      },
    });
  } catch (error) {
    console.error(`[log-bot] Failed to traverse ${filePath}:`, error);
    return null;
  }

  if (!modified) {
    return null;
  }

  ast.program.body.unshift(createLoggerImport());

  const output = generate(ast, { sourceMaps: true }, code);

  return {
    code: output.code,
    map: output.map,
  };
}
