import warnings
from pathlib import Path
from typing import Self

import yaml
from pydantic import BaseModel, Field

from guide import lang, paths
from guide.design import Design


class Guide(BaseModel):
    dir: Path = Field(exclude=True)
    design: Design = Field(default_factory=Design)

    @property
    def lang(self):
        if (self.dir / paths.PYPROJECT_TOML_NAME).exists():
            return lang.py
        elif (self.dir / paths.PACKAGE_JSON_NAME).exists():
            return lang.ts
        else:
            return lang.md

    def load_test_results_(self):
        specs = self.design.flat()
        spec_test_map = {spec.test.ref: spec.test for spec in specs if spec.test}

        for r in self.lang.load_test_results(self.dir):
            spec_test = spec_test_map.get(r.ref)
            if spec_test:
                spec_test.result = r
            else:
                warnings.warn(f"Orphan test result: {r.ref}", stacklevel=2)

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
        if self is None:
            raise FileNotFoundError(
                f"No {paths.GUIDE_YAML_NAME} found in directory hierarchy"
            )
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

        guide.lang.install_claude(guide.dir)
        return guide
