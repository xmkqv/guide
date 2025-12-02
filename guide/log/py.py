def install(patterns: list[str] | None = None) -> None:
    import snoop

    from guide.model import Guide
    from guide.utils import mega_wrap

    if patterns is None:
        guide = Guide.find_nearest()
        if not guide:
            raise RuntimeError("No guide.yaml found for logbot")
        patterns = guide.rgxlog

    snoop.install(builtins=False)
    mega_wrap(patterns, snoop.snoop(depth=1))
