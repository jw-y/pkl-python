from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union
from urllib.parse import urlparse


class PklBugError(Exception):
    pass


class PklError(Exception):
    pass


@dataclass
class ModuleSource:
    uri: str
    text: Optional[str] = None

    @classmethod
    def from_path(cls, path: Union[str, Path]):
        uri = Path(path).absolute().as_uri()
        return cls(uri=uri)

    @classmethod
    def from_text(cls, text: str):
        return cls(uri="repl:text", text=text)

    @classmethod
    def from_uri(cls, uri):
        res = urlparse(uri)
        parsed = res.geturl()
        return cls(uri=parsed)
