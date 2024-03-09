from dataclasses import dataclass
from typing import Any, Optional


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
