import tyro

from . import check, sync, watch


def main():
    cmd = tyro.cli(check.Check | sync.Sync | watch.Watch)
    match cmd:
        case check.Check():
            check.run(cmd)
        case sync.Sync():
            sync.run(cmd)
        case watch.Watch():
            watch.run(cmd)
