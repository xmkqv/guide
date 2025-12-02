import datetime
import difflib
import re
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import cast

from watchfiles import awatch  # type: ignore[import]

from guide.mission import Mission


@dataclass
class Log:
    cache: dict[str, list[str]] = field(default_factory=dict[str, list[str]])
    last_change: float = datetime.datetime.now(tz=datetime.UTC).timestamp()


global log
log = Log()


def on_diff(diff: Iterator[str]) -> None:
    for line in diff:
        print(line, end="")


async def run():
    mission = Mission.load_nearest()

    ideltas = awatch(
        mission.dir,
        debounce=1000,
        watch_filter=watch_filter,
    )
    async for deltas in ideltas:
        for _, path in deltas:
            diff = get_diff(path)
            on_diff(diff)


### Helpers ###

_re_has_dot = re.compile(r"/\.")


def get_diff(path: str):
    lines = Path(path).read_text().splitlines(keepends=True)
    prev = log.cache.get(path) or []
    log.cache[path] = lines

    if prev == lines:
        return cast("Iterator[str]", [])

    return difflib.unified_diff(prev, lines, fromfile=path, tofile=path)


def watch_filter(change: int, path: str) -> bool:
    return not _re_has_dot.search(path)
