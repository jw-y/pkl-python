from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

from pkl.evaluator_options import ClientModuleReader, ClientResourceReader, Project
from pkl.reader import PathElement

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
@dataclass
class IncomingMessage:
    @classmethod
    def decode(cls, incoming: List):
        code, msg = incoming

        if code == CODE_EVALUATE_RESPONSE:
            return EvaluateResponse(**msg)
        elif code == CODE_EVALUATE_LOG:
            return Log(**msg)
        elif code == CODE_NEW_EVALUATOR_RESPONSE:
            return CreateEvaluatorResponse(**msg)
        elif code == CODE_EVALUATE_READ:
            return EvaluatorReadResourceRequest(**msg)
        elif code == CODE_EVALUATE_READ_MODULE:
            return EvaluatorReadModuleRequest(**msg)
        elif code == CODE_LIST_RESOURCES_REQUEST:
            return EvaluatorListResourcesRequest(**msg)
        elif code == CODE_LIST_MODULES_REQUEST:
            return EvaluatorListModulesRequest(**msg)
        else:
            raise ValueError(f"Unknown code: {hex(code)}")


@dataclass
class CreateEvaluatorResponse(IncomingMessage):
    # A number identifying this request
    requestId: int

    # A number identifying the created evaluator.
    evaluatorId: Optional[int] = None

    # A message detailing why the evaluator was not created.
    error: Optional[str] = None


@dataclass
class EvaluateResponse(IncomingMessage):
    # The requestId of the Evaluate request
    requestId: int

    # A number identifying this evaluator.
    evaluatorId: int

    # The evaluation contents, if successful.
    result: Optional[Any] = None

    # A message detailing why evaluation failed.
    error: Optional[str] = None


@dataclass
class Log(IncomingMessage):
    # A number identifying this evaluator.
    evaluatorId: int

    # A number identifying the log level.
    #
    # - 0: trace
    # - 1: warn
    level: int

    # The message to be logged
    message: str

    # A string representing the source location within Pkl code producing this log output.
    frameUri: str


@dataclass
class EvaluatorReadResourceRequest(IncomingMessage):
    # A number identifying this request.
    requestId: int

    # A number identifying this evaluator.
    evaluatorId: int

    # The URI of the resource.
    uri: str


@dataclass
class EvaluatorReadModuleRequest(IncomingMessage):
    # A number identifying this request.
    requestId: int

    # A number identifying this evaluator.
    evaluatorId: int

    # The URI of the module.
    uri: str


@dataclass
class EvaluatorListResourcesRequest(IncomingMessage):
    # A number identifying this request.
    requestId: int

    # A number identifying this evaluator.
    evaluatorId: int

    # The base URI to list resources.
    uri: str


@dataclass
class EvaluatorListModulesRequest(IncomingMessage):
    # A number identifying this request.
    requestId: int

    # A number identifying this evaluator.
    evaluatorId: int

    # The base URI to list modules.
    uri: str


@dataclass
class OutgoingMessage:
    CODE = None

    def _dict_factory(self, items):
        return {k: v for k, v in items if v is not None}

    def to_json(self):
        assert self.CODE is not None
        msg = asdict(self, dict_factory=self._dict_factory)
        obj = [self.CODE, msg]
        return obj


@dataclass
class CreateEvaluator(OutgoingMessage):
    CODE = CODE_NEW_EVALUATOR

    # A number identifying this request
    requestId: int = 0

    # Regex patterns to determine which modules are allowed for import.
    #
    # API version of the CLI's `--allowed-modules` flag
    allowedModules: Optional[List[str]] = None

    # Regex patterns to dettermine which resources are allowed to be read.
    #
    # API version of the CLI's `--allowed-resources` flag
    allowedResources: Optional[List[str]] = None

    # Register client-side module readers.
    clientModuleReaders: Optional[List[ClientModuleReader]] = None

    # Register client-side resource readers.
    clientResourceReaders: Optional[List[ClientResourceReader]] = None

    # Directories, ZIP archives, or JAR archives
    # to search when resolving `modulepath:` URIs.
    #
    # API version of the CLI's `--module-path` flag.
    modulePaths: Optional[List[str]] = None

    # Environment variable to set.
    #
    # API version of the CLI's `--env-var` flag.
    env: Optional[Dict[str, str]] = None

    # External properties to set.
    #
    # API version of the CLI's `--properties` flag.
    properties: Optional[Dict[str, str]] = None

    # Duration, in seconds, after which evaluation of a source module will be timed out.
    #
    # API version of the CLI's `--timeout` flag.
    timeoutSeconds: Optional[int] = None

    # Restricts access to file-based modules and resources to those located under the root directory.
    rootDir: Optional[str] = None

    # The cache directory for storing packages.
    cacheDir: Optional[str] = None

    # The format to generate.
    #
    # This sets the `pkl.outputFormat` external property.
    outputFormat: Optional[str] = None

    # The project dependency settings.
    project: Optional[Project] = None


@dataclass
class CloseEvaluator(OutgoingMessage):
    CODE = CODE_CLOSE_EVALUATOR

    # A number identifying this evaluator.
    evaluatorId: int


@dataclass
class EvaluateRequest(OutgoingMessage):
    CODE = CODE_EVALUATE
    # A number identifying this request
    requestId: int

    # A number identifying this evaluator.
    evaluatorId: int

    # The absolute URI of the module to be evaluated.
    moduleUri: str

    # The module's contents.
    #
    # If [null], Pkl will load the module at runtime.
    moduleText: Optional[str] = None

    # The Pkl expression to be evaluated within the module.
    #
    # If [null], evaluates the whole module.
    expr: Optional[str] = None


@dataclass
class EvaluatorReadResourceResponse(OutgoingMessage):
    CODE = CODE_EVALUATE_READ_RESPONSE

    # A number identifying this request.
    requestId: int

    # A number identifying this evaluator.
    evaluatorId: int

    # The contents of the resource.
    contents: Optional[bytes] = None

    # The description of the error that occured when reading this resource.
    error: Optional[str] = None


@dataclass
class EvaluatorReadModuleResponse(OutgoingMessage):
    CODE = CODE_EVALUATE_READ_MODULE_RESPONSE

    # A number identifying this request.
    requestId: int

    # A number identifying this evaluator.
    evaluatorId: int

    # The string contents of the module.
    contents: Optional[str] = None

    # The description of the error that occured when reading this resource.
    error: Optional[str] = None


@dataclass
class EvaluatorListResourcesResponse(OutgoingMessage):
    CODE = CODE_LIST_RESOURCES_RESPONSE

    # A number identifying this request.
    requestId: int

    # A number identifying this evaluator.
    evaluatorId: int

    # The elements at the provided base path.
    pathElements: Optional[List[PathElement]] = None

    # The description of the error that occured when listing elements.
    error: Optional[str] = None


@dataclass
class EvaluatorListModulesResponse(OutgoingMessage):
    CODE = CODE_LIST_MODULES_RESPONSE

    # A number identifying this request.
    requestId: int

    # A number identifying this evaluator.
    evaluatorId: int

    # The elements at the provided base path.
    pathElements: Optional[List[PathElement]] = None

    # The description of the error that occured when listing elements.
    error: Optional[str] = None
