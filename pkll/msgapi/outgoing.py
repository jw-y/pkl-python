from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional, Union

from pkll.msgapi.code import (
    CODE_CLOSE_EVALUATOR,
    CODE_EVALUATE,
    CODE_EVALUATE_READ_MODULE_RESPONSE,
    CODE_EVALUATE_READ_RESPONSE,
    CODE_LIST_MODULES_RESPONSE,
    CODE_LIST_RESOURCES_RESPONSE,
    CODE_NEW_EVALUATOR,
)


@dataclass
class OutgoingMessage:
    def to_msg_obj(self):
        raise NotImplementedError("Subclasses must implement this method.")


def format_message(msg: OutgoingMessage, code: int):
    msg_dict = asdict(msg)
    filtered_dict = {k: v for k, v in msg_dict.items() if v is not None}
    msg_obj = [code, filtered_dict]
    return msg_obj


@dataclass
class ResourceReader:
    scheme: str
    has_hierarchical_uris: bool
    is_globbable: bool


@dataclass
class ModuleReader:
    scheme: str
    has_hierarchical_uris: bool
    is_globbable: bool
    is_local: bool


@dataclass
class Checksums:
    sha256: str


@dataclass
class PathElement:
    name: str
    is_directory: bool


@dataclass
class ProjectOrDependency:
    package_uri: Optional[str] = None
    type: str = ""
    project_file_uri: Optional[str] = None
    checksums: Optional[Checksums] = None
    dependencies: Dict[str, "ProjectOrDependency"] = field(default_factory=dict)


@dataclass
class ClientResourceReader:
    scheme: str
    hasHierarchicalUris: bool
    isGlobbable: bool


@dataclass
class ClientModuleReader:
    scheme: str
    hasHierarchicalUris: bool
    isGlobbable: bool
    isLocal: bool


@dataclass
class RemoteDependency:
    type: str
    packageUri: Optional[str]
    checksums: Optional[Checksums]


@dataclass
class Project:
    type: str
    packageUri: Optional[str]
    projectFileUri: str
    dependencies: Dict[str, Union["Project", RemoteDependency]]


@dataclass
class CreateEvaluator(OutgoingMessage):
    requestId: int
    allowedModules: Optional[List[str]] = field(default=None)
    allowedResources: Optional[List[str]] = field(default=None)
    clientModuleReaders: Optional[List[ClientModuleReader]] = field(default=None)
    clientResourceReaders: Optional[List[ClientResourceReader]] = field(default=None)
    modulePaths: Optional[List[str]] = field(default=None)
    env: Optional[Dict[str, str]] = field(default=None)
    properties: Optional[Dict[str, str]] = field(default=None)
    timeoutSeconds: Optional[int] = field(default=None)
    rootDir: Optional[str] = field(default=None)
    cacheDir: Optional[str] = field(default=None)
    outputFormat: Optional[str] = field(default=None)
    project: Optional[Project] = field(default=None)

    def to_msg_obj(self):
        return format_message(self, CODE_NEW_EVALUATOR)


@dataclass
class CloseEvaluator(OutgoingMessage):
    evaluatorId: int

    def to_msg_obj(self):
        return format_message(self, CODE_CLOSE_EVALUATOR)


@dataclass
class EvaluateRequest(OutgoingMessage):
    """
    A class to represent a request for evaluating a module or expression in Pkl.

    Attributes:
    - requestId: A number identifying this request.
    - evaluatorId: A number identifying the evaluator.
    - moduleUri: The absolute URI of the module to be evaluated.
    - moduleText: The module's contents. If None, Pkl will load the module at runtime.
    - expr: The Pkl expression to be evaluated within the module. If None, evaluates the whole module.
    """

    requestId: int
    evaluatorId: int
    moduleUri: str
    moduleText: Optional[str] = None
    expr: Optional[str] = None

    def to_msg_obj(self):
        return format_message(self, CODE_EVALUATE)


@dataclass
class EvaluatorReadResourceResponse(OutgoingMessage):
    requestId: int
    evaluatorId: int
    contents: Optional[bytes] = None
    error: Optional[str] = None

    def to_msg_obj(self):
        return format_message(self, CODE_EVALUATE_READ_RESPONSE)


@dataclass
class EvaluatorReadModuleResponse(OutgoingMessage):
    requestId: int
    evaluatorId: int
    contents: Optional[str] = None
    error: Optional[str] = None

    def to_msg_obj(self):
        return format_message(self, CODE_EVALUATE_READ_MODULE_RESPONSE)


@dataclass
class EvaluatorListResourcesResponse(OutgoingMessage):
    requestId: int
    evaluatorId: int
    pathElements: List[PathElement] = field(default_factory=list)
    error: Optional[str] = None

    def to_msg_obj(self):
        return format_message(self, CODE_LIST_RESOURCES_RESPONSE)


@dataclass
class EvaluatorListModulesResponse(OutgoingMessage):
    requestId: int
    evaluatorId: int
    pathElements: List[PathElement] = field(default_factory=list)
    error: Optional[str] = None

    def to_msg_obj(self):
        return format_message(self, CODE_LIST_MODULES_RESPONSE)
