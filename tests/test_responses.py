from pathlib import Path

import pytest

import pkll
from pkll.handler import (
    ListResponse,
    ReadModuleResponse,
    ReadResourceResponse,
    ResourcesHandler,
)
from pkll.msgapi.outgoing import ClientResourceReader


def test_read_modules():
    class CustomModuleHandler(ResourcesHandler):
        def list_response(self, uri: str) -> ListResponse:
            return ListResponse(
                pathElements=[{"name": "foo.pkl", "isDirectory": False}]
            )

        def read_response(self, uri: str) -> ReadResourceResponse:
            return ReadModuleResponse(
                contents="foo = 1",
            )

    _ = pkll.load(
        Path("./tests/myModule.pkl").absolute().as_uri(),
        allowedModules=["pkl:", "repl:", "file:", "customfs:"],
        clientModuleReaders=[
            {
                "scheme": "customfs",
                "hasHierarchicalUris": True,
                "isGlobbable": True,
                "isLocal": True,
            }
        ],
        debug=True,
        module_handler=CustomModuleHandler(),
    )


def test_read_modules_error():
    class CustomModuleHandler(ResourcesHandler):
        def list_response(self, uri: str) -> ListResponse:
            return ListResponse(error="list error")

        def read_response(self, uri: str) -> ReadResourceResponse:
            return ReadModuleResponse(error="read module error")

    with pytest.raises(Exception):
        _ = pkll.load(
            Path("./tests/myModule.pkl").absolute().as_uri(),
            allowedModules=["pkl:", "repl:", "file:", "customfs:"],
            clientModuleReaders=[
                {
                    "scheme": "customfs",
                    "hasHierarchicalUris": True,
                    "isGlobbable": True,
                    "isLocal": True,
                }
            ],
            module_handler=CustomModuleHandler(),
            debug=True,
        )


def test_read_resources():
    class CustomResourceHandler(ResourcesHandler):
        def list_response(self, uri: str) -> ListResponse:
            return ListResponse(
                pathElements=[{"name": "foo.txt", "isDirectory": False}]
            )

        def read_response(self, uri: str) -> ReadResourceResponse:
            return ReadResourceResponse(
                contents=b"Hello, World!",
            )

    _ = pkll.load(
        Path("./tests/with_read.pkl").absolute().as_uri(),
        allowedModules=[
            "pkl:",
            "repl:",
            "file:",
        ],
        allowedResources=[
            "customfs:",
        ],
        clientResourceReaders=[
            ClientResourceReader(
                scheme="customfs",
                hasHierarchicalUris=True,
                isGlobbable=True,
            )
        ],
        debug=True,
        resource_handler=CustomResourceHandler(),
    )
