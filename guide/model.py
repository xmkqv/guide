from pathlib import Path
from typing import Any, Self

import yaml
from pydantic import BaseModel, Field

from guide import lang, paths
from guide.datasets import Datasets
from guide.design import Design
from guide.utils import touch_dir


class Guide(BaseModel):
    dir: Path = Field(exclude=True)
    rgxlog: list[str] = Field(default_factory=list[str])
    design: Design = Field(default_factory=Design)
    datasets: Datasets[Any] | None = None

    @property
    def lang(self):
        if (self.dir / paths.PYPROJECT_TOML_NAME).exists():
            return lang.py
        elif (self.dir / paths.PACKAGE_JSON_NAME).exists():
            return lang.ts
        else:
            return lang.md

    @property
    def results_dir(self):
        return self.dir / paths.RESULTS_DIR_NAME

    @property
    def results_path(self):
        return self.results_dir / self.lang.results_file_name

    @property
    def datasets_dir(self):
        return self.dir / paths.DATASETS_DIR_NAME

    @classmethod
    def find_nearest(cls) -> Self | None:
        current = Path.cwd()
        while current != current.parent:
            candidate = current / paths.GUIDE_YAML_NAME
            if candidate.exists():
                return cls.load(candidate)
            current = current.parent

    @classmethod
    def get_nearest(cls) -> Self:
        self = cls.find_nearest()
        assert self is not None, f"No {paths.GUIDE_YAML_NAME} found"
        return self

    @classmethod
    def load(cls, path: Path) -> Self:
        with path.open("r") as f:
            data = yaml.safe_load(f)
        return cls.model_validate({**data, "dir": path.parent})

    def dump(self) -> None:
        path = self.dir / paths.GUIDE_YAML_NAME
        data = self.model_dump(exclude={"dir"})
        with path.open("w") as f:
            yaml.safe_dump(data, f)

    @classmethod
    def touch(cls):
        guide = cls.find_nearest()

        if not guide:
            guide = Guide(dir=Path.cwd())
            guide.dump()

        touch_dir(guide.results_dir)
        touch_dir(guide.datasets_dir)

        guide.lang.install_claude(guide.dir)

        return guide
