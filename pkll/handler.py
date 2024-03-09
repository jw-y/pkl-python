from dataclasses import dataclass, field
from typing import List, Optional

from pkll.msgapi.outgoing import PathElement


@dataclass
class ListResponse:
    pathElements: List[PathElement] = field(default_factory=list)
    error: Optional[str] = None


@dataclass
class ReadModuleResponse:
    contents: Optional[str] = None
    error: Optional[str] = None


@dataclass
class ReadResourceResponse:
    contents: Optional[bytes] = None
    error: Optional[str] = None


class Handler:
    def list_response(self, uri: str) -> ListResponse:
        raise NotImplementedError


class ModuleHandler(Handler):
    def read_response(self, uri: str) -> ReadModuleResponse:
        raise NotImplementedError


class ResourcesHandler(Handler):
    def read_response(self, uri: str) -> ReadResourceResponse:
        raise NotImplementedError
