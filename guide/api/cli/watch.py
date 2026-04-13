"""Watch mission directory and emit unified diffs on file changes."""

import asyncio
import difflib
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from watchfiles import awatch  # type: ignore[import-untyped]

from guide.model import Guide
from guide.utils import make_watch_filter


@dataclass(frozen=True)
class Watch:
    """
    KEEP THIS FILE, IT IS NICE CODE
    """


def run(_cmd: Watch) -> None:
    asyncio.run(_watch())


type Cache = dict[str, list[str]]


async def _watch() -> None:
    """Watch mission directory, print diffs when files change."""
    mission = Guide.get_nearest()
    cache: Cache = {}
    watch_filter = make_watch_filter(mission.dir)

    async for deltas in awatch(
        mission.dir,
        debounce=1000,
        watch_filter=watch_filter,
    ):
        for _, path in deltas:
            for line in _get_diff(cache, path):
                print(line, end="")  # noqa: T201


def _get_diff(cache: Cache, path: str) -> Iterator[str]:
    """Compute unified diff between cached and current file content."""
    lines = Path(path).read_text().splitlines(keepends=True)
    prev = cache.get(path, [])
    cache[path] = lines
    if prev == lines:
        return cast("Iterator[str]", iter([]))

    return difflib.unified_diff(prev, lines, fromfile=path, tofile=path)
