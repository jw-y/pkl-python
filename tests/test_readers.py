from typing import List

import pytest

import pkl
from pkl import (
    ModuleReader,
    PathElement,
    PklError,
    PreconfiguredOptions,
    ResourceReader,
)


def test_read_modules():
    class TestModuleReader(ModuleReader):
        def read(self, url) -> str:
            return "foo = 1"

        def list_elements(self, url: str) -> List[PathElement]:
            return [PathElement("foo.pkl", False)]

    opts = PreconfiguredOptions(
        moduleReaders=[TestModuleReader("customfs", True, True, True)]
    )
    opts.allowedModules.append("customfs:")
    _ = pkl.load("./tests/myModule.pkl", evaluator_options=opts)


def test_read_modules_error():
    class TestModuleReader(ModuleReader):
        def read(self, url) -> str:
            raise FileNotFoundError("foo.pkl not found")

        def list_elements(self, url: str) -> List[PathElement]:
            return [PathElement("foo.pkl", False)]

    opts = PreconfiguredOptions(
        moduleReaders=[TestModuleReader("customfs", True, True, True)]
    )
    opts.allowedModules.append("customfs:")
    with pytest.raises(PklError):
        _ = pkl.load("./tests/myModule.pkl", evaluator_options=opts)


def test_read_resources():
    class TestResourceReader(ResourceReader):
        def read(self, url) -> bytes:
            return b"Hello, World!"

        def list_elements(self, url: str) -> List[PathElement]:
            return [PathElement("foo.txt", False)]

    opts = PreconfiguredOptions(
        resourceReaders=[
            TestResourceReader(
                scheme="customfs", hasHierarchicalUris=True, isGlobbable=True
            )
        ]
    )
    opts.allowedResources.append("customfs:")

    _ = pkl.load("./tests/with_read.pkl", evaluator_options=opts)
