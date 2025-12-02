"""TypeScript logger bridge.

Generates build-time instrumentation configuration for TypeScript projects.
The actual instrumentation is handled by the unplugin at build time.
"""


def install(patterns: list[str]) -> dict[str, object]:
    """Generate instrumentation config for TypeScript build tooling.

    Returns config dict suitable for unplugin-based instrumentation.
    """
    return {
        "enabled": True,
        "patterns": {"include": [f"/{p}/" for p in patterns]},
        "capture": {"args": True, "return": True, "timing": True, "errors": True},
    }


__all__ = ["install"]
