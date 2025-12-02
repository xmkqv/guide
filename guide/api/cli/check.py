"""Validation hook for Claude Code PostToolUse events."""

import asyncio
import os
import re
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from pydantic import BaseModel
from rich.console import Console
from rich.status import Status


@dataclass(frozen=True)
class Config:
    """Linter configuration paths from environment."""

    biome_config: str = ""
    ruff_config: str = ""
    pyright_config: str = ""
    markdownlint_config: str = ""


def load_config() -> Config:
    """Load configuration from environment variables."""
    return Config(
        biome_config=os.environ.get("BIOME_CONFIG_PATH", ""),
        ruff_config=os.environ.get("RUFF_CONFIG_PATH", ""),
        pyright_config=os.environ.get("PYRIGHT_CONFIG_PATH", ""),
        markdownlint_config=os.environ.get("MARKDOWNLINT_CONFIG_PATH", ""),
    )


class ToolInput(BaseModel):
    """Tool input from Claude Code hook."""

    file_path: str = ""
    old_string: str = ""
    new_string: str = ""
    content: str = ""


class HookData(BaseModel):
    """Hook data from stdin JSON."""

    tool_name: str
    tool_input: ToolInput


class HookSpecificOutput(BaseModel):
    """Output structure for Claude Code hooks."""

    hookEventName: str = "PostToolUse"  # noqa
    decision: str = "approve"
    reason: str = ""
    additionalContext: str = ""  # noqa


class ClaudeCodeHookResponse(BaseModel):
    """Response structure for Claude Code."""

    hookSpecificOutput: HookSpecificOutput  # noqa


@dataclass
class MarkdownIssue:
    """A markdown validation issue."""

    line: int
    column: int
    message: str


@dataclass
class LintResult:
    """Result from running a linter."""

    name: str
    passed: bool
    output: str = ""
    error: str = ""


@dataclass
class ValidationResult:
    """Combined validation results."""

    markdown_issues: list[MarkdownIssue] = field(default_factory=list[MarkdownIssue])
    lint_results: list[LintResult] = field(default_factory=list[LintResult])
    has_errors: bool = False
    formatted_content: str = ""
    was_formatted: bool = False


class Linter(Protocol):
    """Protocol for linter implementations."""

    def name(self) -> str: ...
    def applies(self, ext: str) -> bool: ...
    async def run(self, file_path: str, cfg: Config) -> LintResult: ...


class Formatter(Protocol):
    """Protocol for formatter implementations."""

    def name(self) -> str: ...
    def applies(self, ext: str) -> bool: ...
    async def format(self, file_path: str, cfg: Config) -> None: ...


BOLD_ASTERISK = re.compile(r"\*\*[^*]+\*\*")
BOLD_UNDERSCORE = re.compile(r"__[^_]+__")


def check_markdown_bold(content: str) -> list[MarkdownIssue]:
    """Check for bold text patterns in markdown content."""
    issues: list[MarkdownIssue] = []
    for i, line in enumerate(content.split("\n"), 1):
        for m in BOLD_ASTERISK.finditer(line):
            issue = MarkdownIssue(i, m.start() + 1, f"Bold ** not allowed: {m.group()}")
            issues.append(issue)
        for m in BOLD_UNDERSCORE.finditer(line):
            issue = MarkdownIssue(i, m.start() + 1, f"Bold __ not allowed: {m.group()}")
            issues.append(issue)
    return issues


DEFAULT_TIMEOUT = 30.0


async def run_cmd(name: str, args: list[str]) -> LintResult:
    """Run a command and return the result."""
    try:
        proc = await asyncio.create_subprocess_exec(
            name,
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    except FileNotFoundError:
        return LintResult(name, False, error=f"{name} not found")

    try:
        async with asyncio.timeout(DEFAULT_TIMEOUT):
            stdout, stderr = await proc.communicate()
    except TimeoutError:
        proc.kill()
        await proc.wait()
        return LintResult(name, False, error=f"{name} timed out after {DEFAULT_TIMEOUT}s")

    output = (stdout.decode() + "\n" + stderr.decode()).strip()
    return LintResult(name, proc.returncode == 0, output)


JS_EXTS = frozenset({"js", "jsx", "ts", "tsx", "mjs", "cjs"})
MD_EXTS = frozenset({"md", "markdown"})
PY_EXTS = frozenset({"py", "pyi"})


async def run_biome(file_path: str, cfg: Config) -> LintResult:
    """Run biome check on JS/TS files."""
    args = ["check", "--write"]
    if cfg.biome_config:
        config_dir = (
            Path(cfg.biome_config).parent
            if cfg.biome_config.endswith(".json")
            else cfg.biome_config
        )
        args.append(f"--config-path={config_dir}")
    args.extend(["--vcs-use-ignore-file=false", file_path])
    return await run_cmd("biome", args)


async def run_ruff_format(file_path: str, cfg: Config) -> None:
    """Run ruff format on Python files."""
    args = ["format"]
    if cfg.ruff_config:
        args.append(f"--config={cfg.ruff_config}")
    args.append(file_path)
    await run_cmd("ruff", args)


async def run_ruff_check(file_path: str, cfg: Config) -> LintResult:
    """Run ruff check on Python files."""
    args = ["check", "--fix"]
    if cfg.ruff_config:
        args.append(f"--config={cfg.ruff_config}")
    args.append(file_path)
    return await run_cmd("ruff", args)


async def run_pyright(file_path: str, cfg: Config) -> LintResult:
    """Run pyright on Python files."""
    args: list[str] = []
    if cfg.pyright_config:
        project_dir = Path(cfg.pyright_config).parent
        args.append(f"--project={project_dir}")
    args.append(file_path)
    return await run_cmd("pyright", args)


async def run_markdownlint(file_path: str, cfg: Config) -> LintResult:
    """Run markdownlint on markdown files."""
    args: list[str] = []
    if cfg.markdownlint_config:
        args.extend(["-c", cfg.markdownlint_config])
    args.append(file_path)
    return await run_cmd("markdownlint", args)


def get_ext(file_path: str) -> str:
    """Get file extension without dot."""
    return Path(file_path).suffix.lstrip(".")


def _create_lint_tasks(
    ext: str, tmp_path: str, cfg: Config
) -> list[asyncio.Task[LintResult]]:
    """Create linter tasks based on file extension."""
    if ext in JS_EXTS:
        return [asyncio.create_task(run_biome(tmp_path, cfg))]
    if ext in PY_EXTS:
        return [
            asyncio.create_task(run_ruff_check(tmp_path, cfg)),
            asyncio.create_task(run_pyright(tmp_path, cfg)),
        ]
    if ext in MD_EXTS:
        return [asyncio.create_task(run_markdownlint(tmp_path, cfg))]
    return []


async def _run_linters(
    ext: str, tmp_path: str, cfg: Config, result: ValidationResult
) -> None:
    """Run applicable linters and update result."""
    tasks = _create_lint_tasks(ext, tmp_path, cfg)
    if not tasks:
        return
    lint_results = await asyncio.gather(*tasks)
    result.lint_results = list(lint_results)
    result.has_errors = any(not lr.passed for lr in lint_results) or result.has_errors


async def validate_file(
    file_path: str,
    content: str,
    cfg: Config,
    is_edit: bool = False,
) -> ValidationResult:
    """Validate a file with applicable linters."""
    result = ValidationResult()
    ext = get_ext(file_path)

    if not ext or not content:
        return result

    if ext in MD_EXTS:
        issues = check_markdown_bold(content)
        if issues:
            result.markdown_issues = issues
            result.has_errors = True

    if is_edit:
        return result

    with tempfile.NamedTemporaryFile(mode="w", suffix=f".{ext}", delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        if ext in PY_EXTS:
            await run_ruff_format(tmp_path, cfg)

        await _run_linters(ext, tmp_path, cfg, result)

        formatted = Path(tmp_path).read_text()
        if formatted != content:
            result.formatted_content = formatted
            result.was_formatted = True
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    return result


def _format_markdown_issues(issues: list[MarkdownIssue]) -> list[str]:
    """Format markdown issues for output."""
    lines = ["\nMarkdown validation errors:"]
    lines.extend(
        f"  Line {issue.line}, Col {issue.column}: {issue.message}" for issue in issues
    )
    return lines


def _format_lint_errors(lint_results: list[LintResult]) -> list[str]:
    """Format lint errors for output."""
    lines: list[str] = []
    for lr in lint_results:
        if lr.passed:
            continue
        lines.append(f"\n{lr.name} errors:")
        if lr.output:
            lines.extend(f"  {line}" for line in lr.output.split("\n") if line)
        if lr.error:
            lines.append(f"  Error: {lr.error}")
    return lines


def _build_context(result: ValidationResult) -> list[str]:
    """Build context parts from validation result."""
    parts: list[str] = []
    if result.was_formatted:
        parts.append("Content was auto-formatted")
    if result.markdown_issues:
        parts.extend(_format_markdown_issues(result.markdown_issues))
    parts.extend(_format_lint_errors(result.lint_results))
    return parts


def build_json_response(result: ValidationResult) -> str:
    """Build JSON response for Claude Code."""
    context_parts = _build_context(result)

    if not result.has_errors:
        if not context_parts:
            context_parts.append("All checks passed")
        return ClaudeCodeHookResponse(
            hookSpecificOutput=HookSpecificOutput(
                additionalContext="\n".join(context_parts),
            )
        ).model_dump_json(indent=2)

    context_parts.extend(
        [
            "\n" + "=" * 60,
            "Validation issues found above - please review and address.",
            "=" * 60,
        ]
    )

    return ClaudeCodeHookResponse(
        hookSpecificOutput=HookSpecificOutput(
            reason="Validation completed with issues",
            additionalContext="\n".join(context_parts),
        )
    ).model_dump_json(indent=2)


def _display_lint_errors(console: Console, lint_results: list[LintResult]) -> None:
    """Display lint errors with truncation for readability."""
    for lr in lint_results:
        if lr.passed:
            continue
        console.print(f"\n[red]{lr.name} errors:[/red]")
        if lr.output:
            lines = [line for line in lr.output.split("\n") if line][:10]
            for line in lines:
                console.print(f"  {line}")
        if lr.error:
            console.print(f"  [red]Error: {lr.error}[/red]")


def display_result(console: Console, result: ValidationResult) -> None:
    """Display validation results to stderr."""
    if result.was_formatted:
        console.print("[green]Content was auto-formatted[/green]")

    if not result.has_errors:
        if not result.was_formatted:
            console.print("[green]All checks passed[/green]")
        return

    if result.markdown_issues:
        console.print("\n[red]Markdown validation errors:[/red]")
        for issue in result.markdown_issues:
            console.print(f"  Line {issue.line}, Col {issue.column}: {issue.message}")

    _display_lint_errors(console, result.lint_results)

    console.print("\n" + "=" * 60)
    console.print("[yellow]Validation issues found - please review[/yellow]")
    console.print("=" * 60)


@dataclass
class Check:
    """Run validation on files."""

    files: list[str] = field(default_factory=list[str])
    hook: bool = False


def run(cmd: Check) -> None:
    """Execute the check command."""
    console = Console(stderr=True)
    cfg = load_config()

    if cmd.hook:
        hook_data = HookData.model_validate_json(sys.stdin.read())
        file_path = hook_data.tool_input.file_path

        if not file_path:
            print("{}")  # noqa: T201
            return

        is_edit = hook_data.tool_name == "Edit"
        content = (
            hook_data.tool_input.new_string if is_edit else hook_data.tool_input.content
        )
        full_content = "" if is_edit else hook_data.tool_input.content

        with Status("Validating...", console=console):
            result = asyncio.run(validate_file(file_path, full_content, cfg, is_edit))

        print(build_json_response(result))  # noqa: T201
        display_result(console, result)

    elif cmd.files:
        for file_path in cmd.files:
            path = Path(file_path)
            if not path.exists():
                console.print(f"[red]File not found: {file_path}[/red]")
                continue

            content = path.read_text()
            with Status(f"Validating {file_path}...", console=console):
                result = asyncio.run(validate_file(file_path, content, cfg))

            display_result(console, result)

    else:
        console.print(
            "[yellow]No files specified. Use --hook or provide files.[/yellow]"
        )
