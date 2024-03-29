from dataclasses import asdict, dataclass, field, is_dataclass
from typing import Any, Dict, List, Optional, Union

CODE_NEW_EVALUATOR = 0x20
CODE_NEW_EVALUATOR_RESPONSE = 0x21
CODE_CLOSE_EVALUATOR = 0x22
CODE_EVALUATE = 0x23
CODE_EVALUATE_RESPONSE = 0x24
CODE_EVALUATE_LOG = 0x25
CODE_EVALUATE_READ = 0x26
CODE_EVALUATE_READ_RESPONSE = 0x27
CODE_EVALUATE_READ_MODULE = 0x28
CODE_EVALUATE_READ_MODULE_RESPONSE = 0x29
CODE_LIST_RESOURCES_REQUEST = 0x2A
CODE_LIST_RESOURCES_RESPONSE = 0x2B
CODE_LIST_MODULES_REQUEST = 0x2C
CODE_LIST_MODULES_RESPONSE = 0x2D


# Define the base interface for incoming messages
class IncomingMessage:
    pass


@dataclass
class CreateEvaluatorResponse(IncomingMessage):
    requestId: int
    evaluatorId: Optional[int] = None
    error: Optional[str] = None


@dataclass
class EvaluateResponse(IncomingMessage):
    """
    A class to represent a response to an evaluation request.

    Attributes:
    - requestId (int): The requestId of the Evaluate request.
    - evaluatorId (int): A number identifying the evaluator.
    - result (Optional[Any]): The evaluation contents, if successful. None if evaluation failed.
    - error (Optional[str]): A message detailing why evaluation failed. None if evaluation was successful.
    """

    requestId: int
    evaluatorId: int
    result: Optional[Any] = None
    error: Optional[str] = None


@dataclass
class Log(IncomingMessage):
    evaluatorId: int
    level: int
    message: str
    frameUri: str


@dataclass
class EvaluatorReadResourceRequest(IncomingMessage):
    requestId: int
    evaluatorId: int
    uri: str


@dataclass
class EvaluatorReadModuleRequest(IncomingMessage):
    requestId: int
    evaluatorId: int
    uri: str


@dataclass
class EvaluatorListResourcesRequest(IncomingMessage):
    requestId: int
    evaluatorId: int
    uri: str


@dataclass
class EvaluatorListModulesRequest(IncomingMessage):
    requestId: int
    evaluatorId: int
    uri: str


@dataclass
class OutgoingMessage:
    def to_msg_obj(self):
        raise NotImplementedError("Subclasses must implement this method.")


def dataclass_to_dict(dc):
    if not is_dataclass(dc):
        return dc

    dd = {k: dataclass_to_dict(v) for k, v in asdict(dc).items()}
    return dd


def _filter_dict(dd):
    if not isinstance(dd, dict):
        return dd
    return {k: _filter_dict(v) for k, v in dd.items() if v is not None}


def format_message(msg: OutgoingMessage, code: int):
    # msg_dict = asdict(msg)
    # filtered_dict = {k: v for k, v in msg_dict.items() if v is not None}
    msg_dict = dataclass_to_dict(msg)
    filtered_dict = _filter_dict(msg_dict)
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
    type: str = "remote"
    packageUri: Optional[str] = None
    checksums: Optional[Checksums] = None


@dataclass
class Project:
    projectFileUri: str
    packageUri: Optional[str] = None
    type: str = "local"
    dependencies: Dict[str, Union["Project", RemoteDependency]] = field(
        default_factory=dict
    )


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
