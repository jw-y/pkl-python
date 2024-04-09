import warnings
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List, Optional, Union
from urllib.parse import urlparse

import msgpack

from pkl.evaluator_options import (
    Checksums,
    EvaluatorOptions,
    PreconfiguredOptions,
    RemoteDependency,
)
from pkl.msgapi import (
    CloseEvaluator,
    CreateEvaluator,
    CreateEvaluatorResponse,
    EvaluateRequest,
    EvaluateResponse,
    EvaluatorListModulesRequest,
    EvaluatorListModulesResponse,
    EvaluatorListResourcesRequest,
    EvaluatorListResourcesResponse,
    EvaluatorReadModuleRequest,
    EvaluatorReadModuleResponse,
    EvaluatorReadResourceRequest,
    EvaluatorReadResourceResponse,
    IncomingMessage,
    Log,
    OutgoingMessage,
    Project,
)
from pkl.parser import Parser
from pkl.reader import ModuleReader, ResourceReader
from pkl.server import PKLServer
from pkl.utils import ModuleSource, PklBugError, PklError


class Evaluator:
    def __init__(
        self,
        evaluatorId: int,
        prev_requestId: int,
        manager: "EvaluatorManager",
        resource_readers: Optional[List[ResourceReader]] = None,
        module_readers: Optional[List[ModuleReader]] = None,
        *,
        parser=None,
    ):
        self.evaluatorId = evaluatorId
        self.pending_requests = {}
        self.closed = False
        self._manager = manager
        self._prev_requestId = prev_requestId

        self.resource_readers = resource_readers or []
        self.module_readers = module_readers or []

        self.parser = parser or Parser()

    def _get_requestId(self):
        res = self._prev_requestId + 1
        self._prev_requestId = res
        return res

    def handle_request(self, msg: IncomingMessage):
        if isinstance(msg, EvaluateResponse):
            self.handle_evaluate_response(msg)
        elif isinstance(msg, EvaluatorReadModuleRequest):
            self.handle_read_module(msg)
        elif isinstance(msg, EvaluatorReadResourceRequest):
            self.handle_read_resource(msg)
        elif isinstance(msg, EvaluatorListModulesRequest):
            self.handle_list_modules(msg)
        elif isinstance(msg, EvaluatorListResourcesRequest):
            self.handle_list_resources(msg)
        elif isinstance(msg, Log):
            self.handle_log(msg)
        else:
            raise ValueError(f"Unhandled request: {msg}")

    def evaluate_expression(self, source: ModuleSource, expr: Optional[str]):
        binary_res = self._evaluate_expression_raw(source, expr)
        decoded = msgpack.unpackb(binary_res, strict_map_key=False)
        parsed = self.parser.parse(decoded)
        return parsed

    def _evaluate_expression_raw(self, source: ModuleSource, expr: Optional[str]):
        if self.closed:
            raise ValueError("Evaluator is closed")

        requestId = self._get_requestId()

        request = EvaluateRequest(
            requestId=requestId,
            evaluatorId=self.evaluatorId,
            moduleUri=source.uri,
            moduleText=source.text,
            expr=expr,
        )

        self._manager.send(request)
        response: EvaluateResponse = self._manager.receive(requestId)

        if response.error is not None:
            raise PklError("\n" + response.error)
        return response.result

    def evaluate_module(self, source: ModuleSource):
        return self.evaluate_expression(source, None)

    def evaluate_output_files(self, source: ModuleSource) -> List[str]:
        return self.evaluate_expression(
            source, "output.files.toMap().mapValues((_, it) -> it.text)"
        )

    def evaluate_output_text(self, source: ModuleSource) -> str:
        return self.evaluate_expression(source, "output")

    def evaluate_output_value(self, source: ModuleSource):
        return self.evaluate_expression(source, "output.value")

    def _find_module_reader(
        self, msg: Union[EvaluatorReadModuleRequest, EvaluatorListModulesRequest]
    ):
        uri = urlparse(msg.uri)
        for reader in self.module_readers:
            if reader.scheme == uri.scheme:
                return reader, uri
        raise ValueError(f"No module reader found for scheme '{uri.scheme}'")

    def _find_resource_reader(
        self, msg: Union[EvaluatorReadResourceRequest, EvaluatorListResourcesRequest]
    ):
        uri = urlparse(msg.uri)
        for reader in self.resource_readers:
            if reader.scheme == uri.scheme:
                return reader, uri
        raise ValueError(f"No resource reader found for scheme '{uri.scheme}'")

    def handle_log(self, msg: Log):
        level_map = {
            0: "TRACE",
            1: "WARN",
        }
        s = f"pkl: {level_map[msg.level]}: {msg.message} ({msg.frameUri})"
        if msg.level == 0:
            print(s)
        elif msg.level == 1:
            warnings.warn(s)

    def handle_evaluate_response(self, msg: EvaluateResponse):
        raise NotImplementedError

    def handle_read_resource(self, msg: EvaluatorReadResourceRequest):
        reader, uri = self._find_resource_reader(msg)
        try:
            contents = reader.read(uri.geturl())
            error = None
        except Exception as e:
            contents = None
            error = str(e)
        response = EvaluatorReadResourceResponse(
            msg.requestId, msg.evaluatorId, contents, error
        )
        self._manager.send(response)

    def handle_read_module(self, msg: EvaluatorReadModuleRequest):
        reader, uri = self._find_module_reader(msg)
        try:
            contents = reader.read(uri.geturl())
            error = None
        except Exception as e:
            contents = None
            error = str(e)
        response = EvaluatorReadModuleResponse(
            msg.requestId, msg.evaluatorId, contents, error
        )
        self._manager.send(response)

    def handle_list_resources(self, msg: EvaluatorListResourcesRequest):
        reader, uri = self._find_resource_reader(msg)
        try:
            elements = reader.list_elements(uri.geturl())
            error = None
        except Exception as e:
            elements = None
            error = str(e)
        response = EvaluatorListResourcesResponse(
            msg.requestId, msg.evaluatorId, elements, error
        )
        self._manager.send(response)

    def handle_list_modules(self, msg: EvaluatorListModulesRequest):
        reader, uri = self._find_module_reader(msg)
        try:
            elements = reader.list_elements(uri.geturl())
            error = None
        except Exception as e:
            elements = None
            error = str(e)
        response = EvaluatorListModulesResponse(
            msg.requestId, msg.evaluatorId, elements, error
        )
        self._manager.send(response)

    def close(self):
        request = CloseEvaluator(self.evaluatorId)
        self._manager.send(request)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class EvaluatorManager:
    def __init__(
        self,
        pkl_command: Optional[List[str]] = None,
        *,
        debug=False,
    ):
        self._evaluators: Dict[int, Evaluator] = {}
        self._closed = False
        self._debug = debug
        self._pkl_command = pkl_command
        self._server = PKLServer(pkl_command, debug=debug)

        self._prev_id = -100

    def send(self, msg: OutgoingMessage):
        obj = msg.to_json()
        encoded = msgpack.packb(obj)
        self._server.send(encoded)
        self._server.receive_err()

    def receive(self, requestId) -> IncomingMessage:
        while True:
            msg = self._server.receive()
            self._server.receive_err()
            decoded = IncomingMessage.decode(msg)

            if hasattr(decoded, "requestId") and decoded.requestId == requestId:
                return decoded

            self._evaluators[decoded.evaluatorId].handle_request(decoded)

    def _receive_create_response(self, requestId) -> CreateEvaluatorResponse:
        while True:
            msg = self._server.receive()
            self._server.receive_err()
            decoded = IncomingMessage.decode(msg)

            if (
                isinstance(decoded, CreateEvaluatorResponse)
                and decoded.requestId == requestId
            ):
                return decoded

            # self._evaluators[decoded.evaluatorId].pending_requests[requestId] = decoded
            self._evaluators[decoded.evaluatorId].handle_request(decoded)

    def new_evaluator(
        self, options: EvaluatorOptions, project: Optional[Project] = None, parser=None
    ):
        if self._closed:
            raise ValueError("Server closed")

        requestId = self._get_start_requestId()
        opt_dict = asdict(options)

        opt_dict["clientModuleReaders"] = opt_dict["moduleReaders"]
        opt_dict["clientResourceReaders"] = opt_dict["resourceReaders"]
        del opt_dict["moduleReaders"]
        del opt_dict["resourceReaders"]

        create_evaluator = CreateEvaluator(
            requestId=requestId, project=project, **opt_dict
        )
        self.send(create_evaluator)
        response: CreateEvaluatorResponse = self._receive_create_response(requestId)

        if response.error is not None:
            raise PklBugError(response.error)

        evaluator = Evaluator(
            response.evaluatorId,
            requestId,
            self,
            resource_readers=options.resourceReaders,
            module_readers=options.moduleReaders,
            parser=parser,
        )
        self._evaluators[response.evaluatorId] = evaluator
        return evaluator

    def new_project_evaluator(
        self, project_dir: str, options: EvaluatorOptions, parser=None
    ):
        project_evaluator = self.new_evaluator(PreconfiguredOptions(), parser=parser)
        project = load_project_from_evaluator(project_evaluator, project_dir)
        evaluator = self.new_evaluator(options, project, parser)
        return evaluator

    def _get_start_requestId(self):
        res = self._prev_id + 100
        self._prev_id = res
        return res

    def close(self):
        self._server.terminate()
        self._closed = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def new_evaluator_manager_with_command(pkl_command: List[str]):
    with EvaluatorManager(pkl_command) as manager:
        return manager


def new_evaluator(options: EvaluatorOptions):
    return new_evaluator_with_command(None, options)


def new_evaluator_with_command(
    pkl_command: Optional[List[str]], options: EvaluatorOptions
):
    with EvaluatorManager(pkl_command) as manager:
        return manager.new_evaluator(options)


def new_project_evaluator(project_dir: str, options: EvaluatorOptions):
    return new_project_evaluator_with_command(project_dir, None, options)


def new_project_evaluator_with_command(
    project_dir: str, pkl_command: Optional[List[str]], options: EvaluatorOptions
):
    with EvaluatorManager(pkl_command) as manager:
        project_evaluator = manager.new_evaluator(PreconfiguredOptions())
        project = load_project_from_evaluator(project_evaluator, project_dir)
        return manager.new_evaluator(options, project)


def load_project(path) -> Project:
    with EvaluatorManager() as manager:
        evaluator = manager.new_evaluator(PreconfiguredOptions())
        return load_project_from_evaluator(evaluator, path)


def _encode_dependencies(
    input_dependencies: Dict,
) -> Dict[str, Union[Project, RemoteDependency]]:
    dependencies = {}
    for k, v in input_dependencies.items():
        if v.__class__.__name__ == "Project":
            dependencies[k] = Project(
                v.projectFileUri,
                packageUri=v.package.uri,
                dependencies=_encode_dependencies(v.dependencies),
            )
        elif v.__class__.__name__ == "RemoteDependency":
            dependencies[k] = RemoteDependency(
                packageUri=v.uri, checksums=Checksums(v.checksums.sha256)
            )
        else:
            raise ValueError(f"Unknown dependency: {v.__class__.__name__}")
    return dependencies


def load_project_from_evaluator(evaluator: Evaluator, path) -> Project:
    path = str(Path(path) / "PklProject")
    config = evaluator.evaluate_output_value(ModuleSource.from_path(path))
    dependencies = _encode_dependencies(config.dependencies)
    project = Project(config.projectFileUri, dependencies=dependencies)
    return project
