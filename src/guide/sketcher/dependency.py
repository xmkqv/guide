"""Module dependency graph sketch."""

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from .base import SketchConfig, SketchResult
from .utils import parse_imports, walk_python_files


@dataclass(frozen=True)
class Config(SketchConfig):
    """Configuration for dependency graph sketch."""

    format: Literal["mermaid", "ascii"] = "mermaid"
    exclude: tuple[str, ...] = (
        "__pycache__",
        ".git",
        ".venv",
        "node_modules",
        "tests",
        ".pytest_cache",
    )
    internal_only: bool = True
    max_depth: int = 2


def sketch(config: Config) -> SketchResult:
    """Generate module dependency graph."""
    # Discover project structure
    root = config.path
    py_files = list(walk_python_files(root, exclude=config.exclude))

    # Find src directories to determine package roots
    package_roots = _find_package_roots(root)

    # Build dependency graph
    edges: set[tuple[str, str]] = set()
    modules: set[str] = set()

    for py_file in py_files:
        module_name = _path_to_module(py_file, package_roots)
        if not module_name:
            continue

        modules.add(module_name)
        imports = parse_imports(py_file)

        for imp in imports:
            if imp.is_relative:
                # Resolve relative import
                target = _resolve_relative(module_name, imp.module, imp.level)
            else:
                target = imp.module

            if not target:
                continue

            # Filter to internal modules only if configured
            if config.internal_only:
                if not _is_internal(target, package_roots):
                    continue

            # Truncate to max_depth
            source_short = _truncate_module(module_name, config.max_depth)
            target_short = _truncate_module(target, config.max_depth)

            if source_short != target_short:
                edges.add((source_short, target_short))

    if config.format == "mermaid":
        content = _render_mermaid(edges)
    else:
        content = _render_ascii(edges)

    return SketchResult(
        name="dependency",
        format=config.format,
        content=content,
    )


def _find_package_roots(root: Path) -> list[Path]:
    """Find src directories or direct package directories."""
    roots: list[Path] = []

    # Check for src layout
    src_dir = root / "src"
    if src_dir.exists():
        roots.append(src_dir)

    # Check for libs with nested src layouts
    libs_dir = root / "libs"
    if libs_dir.exists():
        for lib in libs_dir.iterdir():
            if lib.is_dir():
                lib_src = lib / "src"
                if lib_src.exists():
                    roots.append(lib_src)

    # Fallback to root if no src found
    if not roots:
        roots.append(root)

    return roots


def _path_to_module(path: Path, package_roots: list[Path]) -> str:
    """Convert file path to module name."""
    for root in package_roots:
        try:
            rel = path.relative_to(root)
            parts = list(rel.parts)
            if parts[-1] == "__init__.py":
                parts = parts[:-1]
            elif parts[-1].endswith(".py"):
                parts[-1] = parts[-1][:-3]
            return ".".join(parts)
        except ValueError:
            continue
    return ""


def _resolve_relative(current: str, target: str, level: int) -> str:
    """Resolve relative import to absolute module name."""
    parts = current.split(".")
    if level > len(parts):
        return ""
    base = parts[: -level] if level > 0 else parts
    if target:
        return ".".join([*base, target])
    return ".".join(base)


def _is_internal(module: str, package_roots: list[Path]) -> bool:
    """Check if module is internal to the project."""
    # Get top-level package names from roots
    internal_packages: set[str] = set()
    for root in package_roots:
        for child in root.iterdir():
            if child.is_dir() and (child / "__init__.py").exists():
                internal_packages.add(child.name)

    top_level = module.split(".")[0]
    return top_level in internal_packages


def _truncate_module(module: str, depth: int) -> str:
    """Truncate module path to specified depth."""
    parts = module.split(".")
    return ".".join(parts[:depth])


def _render_mermaid(edges: set[tuple[str, str]]) -> str:
    """Render edges as Mermaid flowchart."""
    if not edges:
        return "graph TD\n    empty[No dependencies found]"

    lines = ["graph TD"]

    # Group by source for cleaner output
    by_source: dict[str, list[str]] = defaultdict(list)
    for source, target in sorted(edges):
        by_source[source].append(target)

    for source in sorted(by_source):
        source_id = _mermaid_id(source)
        for target in sorted(by_source[source]):
            target_id = _mermaid_id(target)
            lines.append(f"    {source_id}[{source}] --> {target_id}[{target}]")

    return "\n".join(lines)


def _render_ascii(edges: set[tuple[str, str]]) -> str:
    """Render edges as ASCII text."""
    if not edges:
        return "(no dependencies)"

    lines: list[str] = []
    by_source: dict[str, list[str]] = defaultdict(list)
    for source, target in sorted(edges):
        by_source[source].append(target)

    for source in sorted(by_source):
        lines.append(f"{source}")
        targets = sorted(by_source[source])
        for i, target in enumerate(targets):
            prefix = "└── " if i == len(targets) - 1 else "├── "
            lines.append(f"  {prefix}{target}")

    return "\n".join(lines)


def _mermaid_id(name: str) -> str:
    """Convert module name to valid Mermaid ID."""
    return name.replace(".", "_").replace("-", "_")
