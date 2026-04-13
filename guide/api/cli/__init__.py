import tyro

from . import check, drift, hooks, portal, sync, watch


def main():
    cmd = tyro.cli(
        check.Check
        | sync.Sync
        | watch.Watch
        | portal.Portal
        | drift.Drift
        | hooks.Hooks
    )
    match cmd:
        case check.Check():
            return check.run(cmd)
        case sync.Sync():
            return sync.run(cmd)
        case watch.Watch():
            return watch.run(cmd)
        case portal.Portal():
            return portal.run(cmd)
        case drift.Drift():
            return drift.run(cmd)
        case hooks.Hooks():
            return hooks.run(cmd)
