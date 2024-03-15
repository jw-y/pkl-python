import os
import warnings
from collections import deque
from typing import Dict, List, Optional

import msgpack

from pkll.handler import ModuleHandler, ResourcesHandler
from pkll.msgapi.code import (
    CODE_EVALUATE_LOG,
    CODE_EVALUATE_READ,
    CODE_EVALUATE_READ_MODULE,
    CODE_EVALUATE_RESPONSE,
    CODE_LIST_MODULES_REQUEST,
    CODE_LIST_RESOURCES_REQUEST,
)
from pkll.msgapi.incoming import (
    CreateEvaluatorResponse,
    EvaluateResponse,
    EvaluatorListModulesRequest,
    EvaluatorListResourcesRequest,
    EvaluatorReadModuleRequest,
    EvaluatorReadResourceRequest,
    Log,
)
from pkll.msgapi.outgoing import (
    ClientModuleReader,
    ClientResourceReader,
    CloseEvaluator,
    CreateEvaluator,
    EvaluateRequest,
    EvaluatorListModulesResponse,
    EvaluatorListResourcesResponse,
    EvaluatorReadModuleResponse,
    EvaluatorReadResourceResponse,
    Project,
)
from pkll.parser import Parser
from pkll.server import PKLServer

EVALUATOR_DEFAULT = "DEFAULT"


class Evaluator:
    def __init__(
        self,
        allowedModules: Optional[List[str]] = [
            "pkl:",
            "file:",
            "modulepath:",
            "https:",
            "repl:",
            "package:",
            "projectpackage:",
        ],
        allowedResources: Optional[List[str]] = [
            "env:",
            "prop:",
            "package:",
            "projectpackage:",
        ],
        clientModuleReaders: Optional[List[ClientModuleReader]] = None,
        clientResourceReaders: Optional[List[ClientResourceReader]] = None,
        modulePaths: Optional[List[str]] = None,
        env: Optional[Dict[str, str]] = EVALUATOR_DEFAULT,
        properties: Optional[Dict[str, str]] = None,
        timeoutSeconds: Optional[int] = None,
        rootDir: Optional[str] = None,
        cacheDir: Optional[str] = EVALUATOR_DEFAULT,
        outputFormat: Optional[str] = None,
        project: Optional[Project] = None,
        debug=False,
    ):
        self._server = PKLServer()
        self._evaluator_id = None

        if env == EVALUATOR_DEFAULT:
            env = dict(os.environ)

        if cacheDir == EVALUATOR_DEFAULT:
            dirname = os.path.expanduser("~")
            defaultCacheDir = os.path.join(dirname, ".pkl", "cache")
            cacheDir = defaultCacheDir

        self._CreateEvaluatorOpts = CreateEvaluator(
            requestId=self._server.get_request_id(),
            allowedModules=allowedModules,
            allowedResources=allowedResources,
            clientModuleReaders=clientModuleReaders,
            clientResourceReaders=clientResourceReaders,
            modulePaths=modulePaths,
            env=env,
            properties=properties,
            timeoutSeconds=timeoutSeconds,
            rootDir=rootDir,
            cacheDir=cacheDir,
            outputFormat=outputFormat,
            project=project,
        )
        self._debug = debug

    def create(self):
        self._server.start_process(debug=self._debug)

        msg_obj = self._CreateEvaluatorOpts.to_msg_obj()
        responses = self._handle_send_and_receive(msg_obj)
        assert len(responses) == 1
        code, msg_body = responses[0]

        response = CreateEvaluatorResponse(**msg_body)
        self._evaluator_id = response.evaluatorId
        return response

    def close(self):
        if self._evaluator_id is None:
            raise ValueError("Evaluator not created")

        msg_obj = CloseEvaluator(self._evaluator_id).to_msg_obj()
        _ = self._server.send_and_receive(msg_obj)

    def terminate(self):
        self._server.terminate()

    def _emit_logs(self, responses):
        ex_log = []

        for res in responses:
            is_log = res[0] == CODE_EVALUATE_LOG
            if is_log:
                self._handle_log_message(res)
            else:
                ex_log.append(res)

        return ex_log

    def _handle_send_and_receive(self, msg_obj) -> List:
        responses = self._server.send_and_receive(msg_obj)
        responses = self._emit_logs(responses)

        while len(responses) == 0:
            responses = self._server.receive_with_retry()
            responses = self._emit_logs(responses)
        return responses

    def _handle_log_message(self, response: List):
        code, msg_body = response
        response = Log(**msg_body)
        level_map = {
            0: "TRACE",
            1: "WARN",
        }
        msg = f"pkl: {level_map[response.level]}: {response.message} ({response.frameUri})"
        if response.level == 0:
            print(msg)
        elif response.level == 1:
            warnings.warn(msg)

    def request(
        self,
        moduleUri: str,
        moduleText=None,
        expr=None,
        force_render=False,
        parser=None,
        module_handler: Optional[ModuleHandler] = None,
        resource_handler: Optional[ResourcesHandler] = None,
    ):
        parser = parser or Parser(force_render=force_render)

        msg_obj = EvaluateRequest(
            requestId=self._server.get_request_id(),
            evaluatorId=self._evaluator_id,
            moduleUri=moduleUri,
            moduleText=moduleText,
            expr=expr,
        ).to_msg_obj()

        all_responses = self._handle_send_and_receive(msg_obj)

        queue = deque()
        queue.extend(all_responses)
        results = []

        while queue:
            code, msg_body = queue.popleft()
            if code == CODE_EVALUATE_RESPONSE:
                response = EvaluateResponse(**msg_body)

                if response.error:
                    raise Exception(response.error)
                raw = response.result
                result = msgpack.unpackb(raw, strict_map_key=False)
                parsed = parser.parse(result)
                results.append(parsed)
            elif code == CODE_LIST_MODULES_REQUEST:
                request = EvaluatorListModulesRequest(**msg_body)
                if module_handler is None:
                    raise ValueError("'module_handler' not given")
                res = module_handler.list_response(request.uri)
                msg_obj = EvaluatorListModulesResponse(
                    requestId=request.requestId,
                    evaluatorId=request.evaluatorId,
                    pathElements=res.pathElements,
                    error=res.error,
                ).to_msg_obj()
                all_responses = self._handle_send_and_receive(msg_obj)
                queue.extend(all_responses)
            elif code == CODE_LIST_RESOURCES_REQUEST:
                request = EvaluatorListResourcesRequest(**msg_body)
                if resource_handler is None:
                    raise ValueError("'resource_handler' not given")
                res = resource_handler.list_response(request.uri)
                msg_obj = EvaluatorListResourcesResponse(
                    requestId=request.requestId,
                    evaluatorId=request.evaluatorId,
                    pathElements=res.pathElements,
                    error=res.error,
                ).to_msg_obj()
                all_responses = self._handle_send_and_receive(msg_obj)
                queue.extend(all_responses)
            elif code == CODE_EVALUATE_READ_MODULE:
                request = EvaluatorReadModuleRequest(**msg_body)
                if module_handler is None:
                    raise ValueError("'module_handler' not given")
                res = module_handler.read_response(request.uri)
                msg_obj = EvaluatorReadModuleResponse(
                    requestId=request.requestId,
                    evaluatorId=request.evaluatorId,
                    contents=res.contents,
                    error=res.error,
                ).to_msg_obj()
                all_responses = self._handle_send_and_receive(msg_obj)
                queue.extend(all_responses)
            elif code == CODE_EVALUATE_READ:
                request = EvaluatorReadResourceRequest(**msg_body)
                if resource_handler is None:
                    raise ValueError("'resource_handler' not given")
                res = resource_handler.read_response(request.uri)
                msg_obj = EvaluatorReadResourceResponse(
                    requestId=request.requestId,
                    evaluatorId=request.evaluatorId,
                    contents=res.contents,
                    error=res.error,
                ).to_msg_obj()
                all_responses = self._handle_send_and_receive(msg_obj)
                queue.extend(all_responses)
            else:
                raise NotImplementedError(f"code: {hex(code)}")

        assert len(results) == 1
        return results[0]

    def __enter__(self):
        self.create()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        self.terminate()
