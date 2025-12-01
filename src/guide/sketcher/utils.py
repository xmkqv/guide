"""Shared utilities for sketch modules."""

import ast
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ImportInfo:
    """Extracted import information."""

    module: str
    is_relative: bool
    level: int  # Number of dots for relative imports


@dataclass(frozen=True)
class TypeInfo:
    """Extracted type/class information."""

    name: str
    kind: str  # "dataclass", "attrs", "pydantic", "namedtuple", "class"
    fields: tuple[str, ...]
    bases: tuple[str, ...]


def walk_python_files(
    root: Path,
    exclude: tuple[str, ...] = ("__pycache__", ".git", "node_modules", ".venv"),
) -> Iterator[Path]:
    """Yield Python files under root, excluding specified directories."""
    for path in root.rglob("*.py"):
        if any(part in exclude for part in path.parts):
            continue
        yield path


def parse_imports(path: Path) -> list[ImportInfo]:
    """Extract import statements from a Python file."""
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
    except (SyntaxError, UnicodeDecodeError):
        return []

    imports: list[ImportInfo] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(
                ImportInfo(module=alias.name, is_relative=False, level=0)
                for alias in node.names
            )
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            imports.append(
                ImportInfo(module=module, is_relative=node.level > 0, level=node.level)
            )

    return imports


def find_types(path: Path) -> list[TypeInfo]:
    """Find class/dataclass/attrs definitions in a Python file."""
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
    except (SyntaxError, UnicodeDecodeError):
        return []

    types: list[TypeInfo] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue

        kind = _classify_type(node)
        fields = _extract_fields(node, kind)
        bases = tuple(_base_name(b) for b in node.bases)

        types.append(TypeInfo(name=node.name, kind=kind, fields=fields, bases=bases))

    return types


def _classify_type(node: ast.ClassDef) -> str:
    """Determine the kind of class definition."""
    decorators = [_decorator_name(d) for d in node.decorator_list]

    if "dataclass" in decorators or "dataclasses.dataclass" in decorators:
        return "dataclass"
    if any(d.startswith("attrs") or d in ("frozen", "define") for d in decorators):
        return "attrs"
    if any("pydantic" in d.lower() or d == "BaseModel" for d in decorators):
        return "pydantic"

    # Check bases for pydantic
    bases = [_base_name(b) for b in node.bases]
    if "BaseModel" in bases:
        return "pydantic"
    if "NamedTuple" in bases or "typing.NamedTuple" in bases:
        return "namedtuple"

    return "class"


def _decorator_name(node: ast.expr) -> str:
    """Extract decorator name as string."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{_decorator_name(node.value)}.{node.attr}"
    if isinstance(node, ast.Call):
        return _decorator_name(node.func)
    return ""


def _base_name(node: ast.expr) -> str:
    """Extract base class name as string."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Subscript):
        return _base_name(node.value)
    return ""


def _extract_fields(node: ast.ClassDef, kind: str) -> tuple[str, ...]:
    """Extract field names from a class definition."""
    fields: list[str] = []

    for item in node.body:
        # Annotated assignments (typical for dataclass/attrs/pydantic)
        if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
            fields.append(item.target.id)
        # Regular assignments (less common but possible)
        elif isinstance(item, ast.Assign):
            fields.extend(
                target.id
                for target in item.targets
                if isinstance(target, ast.Name) and not target.id.startswith("_")
            )

    return tuple(fields)


def build_tree_ascii(
    root: Path,
    max_depth: int = 4,
    exclude: tuple[str, ...] = ("__pycache__", ".git", "node_modules", ".venv"),
    _prefix: str = "",
    _depth: int = 0,
) -> str:
    """Build ASCII tree representation of directory structure."""
    if _depth > max_depth:
        return ""

    lines: list[str] = []

    if _depth == 0:
        lines.append(root.name + "/")

    try:
        entries = sorted(root.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
    except PermissionError:
        return ""

    # Filter excluded
    entries = [e for e in entries if e.name not in exclude]

    for i, entry in enumerate(entries):
        is_last = i == len(entries) - 1
        connector = "└── " if is_last else "├── "
        suffix = "/" if entry.is_dir() else ""

        lines.append(f"{_prefix}{connector}{entry.name}{suffix}")

        if entry.is_dir():
            extension = "    " if is_last else "│   "
            subtree = build_tree_ascii(
                entry,
                max_depth=max_depth,
                exclude=exclude,
                _prefix=_prefix + extension,
                _depth=_depth + 1,
            )
            if subtree:
                lines.append(subtree)

    return "\n".join(lines)
