from pathlib import Path

from guide.utils import AutoDir

GUIDE_YAML_NAME = "guide.yaml"
DATASETS_DIR_NAME = "datasets"
RESULTS_DIR_NAME = "results"

PYPROJECT_TOML_NAME = "pyproject.toml"
PACKAGE_JSON_NAME = "package.json"

###

this_file = Path(__file__).resolve()
GUIDES_DIR = this_file.parent.parent / "guides"

###


class Preferences(AutoDir, base=GUIDES_DIR / "preferences"):
    py = "py.md"
    ts = "ts.md"
    code = "code.md"
    ml = "ml.md"
    meta = "meta.md"
    prose = "prose.md"


class Commands(AutoDir, base=GUIDES_DIR / "agents"):
    gen_art = "gen-art.md"
    gen_limn = "gen-limn.md"
    gen_mission = "gen-mission.md"
    gen_mood = "gen-mood.md"
