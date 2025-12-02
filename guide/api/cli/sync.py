import asyncio
from dataclasses import dataclass

from guide.model import Guide


@dataclass(frozen=True)
class Sync:
    tests: bool = False
    limns: bool = False
    report: bool = False


async def _run_sync(cmd: Sync):
    guide = Guide.touch()

    # tests + limns - consume async generators
    specs = guide.design.flat()
    for spec in specs:
        async for _ in spec.sync(tests=cmd.tests, limns=cmd.limns):
            pass

    # report - consume async generator
    async for _ in guide.design.sync(report=cmd.report):
        pass


def run(cmd: Sync):
    asyncio.run(_run_sync(cmd))
