from pydantic import BaseModel, Field

from . import py, ts


class Logger(BaseModel):
    patterns: list[str] = Field(default_factory=list)

    def install(self, language: str) -> dict[str, object] | None:
        if language == "py":
            py.install(self.patterns)
            return None
        elif language == "ts":
            return ts.install(self.patterns)
        else:
            raise ValueError(f"Unsupported language for logger: {language}")


def install(patterns: list[str], language: str) -> dict[str, object] | None:
    if language == "py":
        py.install(patterns)
        return None
    elif language == "ts":
        return ts.install(patterns)
    else:
        raise ValueError(f"Unsupported language for logger: {language}")


__all__ = ["Logger", "install"]
