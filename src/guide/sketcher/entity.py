"""Domain entity diagram sketch."""

from collections import defaultdict
from dataclasses import dataclass
from typing import Literal

from .base import SketchConfig, SketchResult
from .utils import TypeInfo, find_types, walk_python_files


@dataclass(frozen=True)
class Config(SketchConfig):
    """Configuration for entity diagram sketch."""

    format: Literal["mermaid", "ascii"] = "mermaid"
    exclude: tuple[str, ...] = (
        "__pycache__",
        ".git",
        ".venv",
        "node_modules",
        "tests",
        ".pytest_cache",
    )
    include_kinds: tuple[str, ...] = ("dataclass", "attrs", "pydantic", "namedtuple")


def sketch(config: Config) -> SketchResult:
    """Generate domain entity diagram."""
    py_files = list(walk_python_files(config.path, exclude=config.exclude))

    # Collect all types
    all_types: list[tuple[str, TypeInfo]] = []
    for py_file in py_files:
        types = find_types(py_file)
        module = py_file.stem
        all_types.extend(
            (module, t) for t in types if t.kind in config.include_kinds
        )

    # Build type name set for relationship detection
    type_names = {t.name for _, t in all_types}

    # Detect relationships from field types
    relationships: list[tuple[str, str, str]] = []  # (from, to, label)
    for _, t in all_types:
        for field in t.fields:
            # Check if field name hints at a type reference
            field_upper = _to_pascal(field)
            if field_upper in type_names and field_upper != t.name:
                relationships.append((t.name, field_upper, field))

        # Check base classes
        relationships.extend(
            (t.name, base, "extends") for base in t.bases if base in type_names
        )

    if config.format == "mermaid":
        content = _render_mermaid(all_types, relationships)
    else:
        content = _render_ascii(all_types, relationships)

    return SketchResult(
        name="entity",
        format=config.format,
        content=content,
    )


def _to_pascal(name: str) -> str:
    """Convert snake_case to PascalCase."""
    return "".join(word.capitalize() for word in name.split("_"))


def _group_by_module(types: list[tuple[str, TypeInfo]]) -> dict[str, list[TypeInfo]]:
    """Group types by their module."""
    by_module: dict[str, list[TypeInfo]] = defaultdict(list)
    for module, t in types:
        by_module[module].append(t)
    return by_module


def _render_entity_fields(t: TypeInfo, max_fields: int = 8) -> list[str]:
    """Render entity fields as Mermaid lines."""
    lines = [f"        string {field}" for field in t.fields[:max_fields]]
    if len(t.fields) > max_fields:
        lines.append(f"        string ...{len(t.fields) - max_fields}_more")
    return lines


def _render_mermaid(
    types: list[tuple[str, TypeInfo]],
    relationships: list[tuple[str, str, str]],
) -> str:
    """Render as Mermaid erDiagram."""
    if not types:
        return "erDiagram\n    EMPTY[No domain types found]"

    lines = ["erDiagram"]
    by_module = _group_by_module(types)

    # Render entities with fields
    for module in sorted(by_module):
        lines.append(f"    %% {module}")
        for t in sorted(by_module[module], key=lambda x: x.name):
            lines.append(f"    {t.name} {{")
            lines.extend(_render_entity_fields(t))
            lines.append("    }")

    # Render relationships
    lines.extend(_render_mermaid_relationships(relationships))

    return "\n".join(lines)


def _render_mermaid_relationships(
    relationships: list[tuple[str, str, str]],
) -> list[str]:
    """Render relationships as Mermaid lines."""
    if not relationships:
        return []

    lines = ["    %% relationships"]
    seen: set[tuple[str, str]] = set()
    for from_type, to_type, label in relationships:
        key = (from_type, to_type)
        if key not in seen:
            connector = "||--||" if label == "extends" else "||--o{"
            rel_label = "extends" if label == "extends" else "has"
            lines.append(f"    {from_type} {connector} {to_type} : {rel_label}")
            seen.add(key)
    return lines


def _render_ascii(
    types: list[tuple[str, TypeInfo]],
    relationships: list[tuple[str, str, str]],
) -> str:
    """Render as ASCII text."""
    if not types:
        return "(no domain types found)"

    lines: list[str] = []
    by_module = _group_by_module(types)

    for module in sorted(by_module):
        lines.append(f"[{module}]")
        for t in sorted(by_module[module], key=lambda x: x.name):
            kind_marker = {"dataclass": "@dc", "attrs": "@at", "pydantic": "@pd"}.get(
                t.kind, ""
            )
            lines.append(f"  {t.name} {kind_marker}")
            lines.extend(f"    - {field}" for field in t.fields[:6])
            if len(t.fields) > 6:
                lines.append(f"    - ...{len(t.fields) - 6} more")
        lines.append("")

    if relationships:
        lines.append("[relationships]")
        lines.extend(
            f"  {from_type} -> {to_type} ({label})"
            for from_type, to_type, label in relationships
        )

    return "\n".join(lines)
