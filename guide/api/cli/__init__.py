import tyro

from . import check, portal, sync, watch


def main():
    cmd = tyro.cli(check.Check | sync.Sync | watch.Watch | portal.Portal)
    match cmd:
        case check.Check():
            return check.run(cmd)
        case sync.Sync():
            return sync.run(cmd)
        case watch.Watch():
            return watch.run(cmd)
        case portal.Portal():
            return portal.run(cmd)
