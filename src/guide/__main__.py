from watchfiles import watch

from guide.mission import Mission


def main():
    mission = Mission.load_nearest()
    for deltas in watch(
        mission.dir,
        watch_filter=None,
        debounce=1000,
        debug=False,
    ):
        for delta in deltas:
            print("File change detected:", delta)


if __name__ == "__main__":
    main()
