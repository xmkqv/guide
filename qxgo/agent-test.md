# Agent Testing Instructions for qxgo Validation Hook

## Purpose

Test that the PostToolUse validation hook is working correctly by creating files with intentional errors.

## Expected Behavior

- Files should be written successfully (exit 0)
- Validation warnings should be displayed after each write
- Hook should NOT block the write operation

## Test Cases

### Test 1: Markdown with Bold Text

Create a file with bold formatting (should trigger custom validator).
Use double-asterisk bold and double-underscore bold syntax.

File: `/tmp/test-bold.md`

Content:

- Line 1: `# Test Document`
- Line 2: Empty
- Line 3: `This text has [DOUBLE-ASTERISK]bold formatting[DOUBLE-ASTERISK] which should be flagged.`
- Line 4: Empty
- Line 5: `And here's [DOUBLE-UNDERSCORE]another bold[DOUBLE-UNDERSCORE] style.`

Replace [DOUBLE-ASTERISK] with two asterisks and [DOUBLE-UNDERSCORE] with two underscores.

Expected warnings:

- Line X, Col Y: Bold text using asterisks is not allowed
- Line X, Col Y: Bold text using underscores is not allowed

---

### Test 2: Markdown Missing Trailing Newline

Create a markdown file without trailing newline (should trigger markdownlint):

```text
# Test

This file has no trailing newline
```

File: `/tmp/test-newline.md`

Expected warnings:

- markdownlint: MD047/single-trailing-newline

---

### Test 3: TypeScript with Formatting Issues

Create a TypeScript file with formatting issues (should trigger biome):

```typescript
const greeting:string="hello"
console.log(greeting)
```

File: `/tmp/test-format.ts`

Expected warnings:

- biome formatter would change quotes to single quotes
- biome formatter would add semicolons
- biome formatter would add trailing newline

---

### Test 4: TypeScript with Linting Issues

Create a TypeScript file with linting issues (should trigger biome):

```typescript
const x: any = 'test';
let unused = 42;
console.log(x);
```

File: `/tmp/test-lint.ts`

Expected warnings:

- biome: noExplicitAny error
- biome: noUnusedVariables error

---

### Test 5: Python with Quote Style Issues

Create a Python file with quote style issues (should trigger ruff):

```python
def greet(name: str) -> str:
    return f'Hello, {name}!'

print(greet('World'))
```

File: `/tmp/test-quotes.py`

Expected warnings:

- ruff: Q000 Single quotes found but double quotes preferred

---

### Test 6: Python with Type Issues

Create a Python file with type issues (should trigger pyright):

```python
def add(a: int, b: int) -> int:
    return a + b

result: str = add(1, 2)
```

File: `/tmp/test-types.py`

Expected warnings:

- pyright: Type mismatch (int vs str)

---

### Test 7: Valid File (No Warnings)

Create a properly formatted file:

```typescript
const greeting: string = 'Hello, World!';
console.log(greeting);
```

File: `/tmp/test-valid.ts`

Expected output:

- All checks passed (checkmark)

---

### Test 8: Multiple Issues in One File

Create a markdown file with multiple validation issues using bold syntax and missing trailing newline.

File: `/tmp/test-multiple.md`

Expected warnings:

- Multiple markdown bold text violations
- markdownlint trailing newline issue

---

## Instructions for Agent

For each test case above:

1. Create the file using the Write tool with the content shown
2. Observe the output - you should see validation warnings
3. Verify the file exists - check that the file was written despite warnings
4. Report results - confirm that:
   - File was created successfully
   - Validation warnings appeared
   - Hook did NOT block the operation

## Success Criteria

- All files are created successfully
- Validation warnings appear after each write
- Exit code is 0 for all operations
- Agent can see the validation feedback

## Notes

- The hook runs after Write/Edit operations
- Validation issues are informational only
- Files are never blocked from being written
- Missing linters also return exit 0 with warning message
