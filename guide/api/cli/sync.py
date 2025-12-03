from dataclasses import dataclass

from logbot import log

from guide.model import Guide


@dataclass(frozen=True)
class Sync:
    pass


@dataclass(frozen=True)
class SyncResult:
    declared: set[str]
    discovered: set[str]

    @property
    def undeclared(self) -> set[str]:
        return self.discovered - self.declared


def run(cmd: Sync) -> SyncResult:
    guide = Guide.touch()
    guide.load_test_results_()

    declared = {spec.test.ref for spec in guide.design.flat() if spec.test}
    discovered = set(guide.lang.discover_tests(guide.dir))

    result = SyncResult(declared=declared, discovered=discovered)

    for ref in sorted(result.undeclared):
        log.warning(f"Undeclared test: {ref}")

    return result
