# Code generated from Pkl module `MyModule`. DO NOT EDIT.
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, Set, Union

import pkl


@dataclass
class MyModule:
    foo: str

    _registered_identifier = "MyModule"

    @classmethod
    def load_pkl(cls, source):
        # Load the Pkl module at the given source and evaluate it into `MyModule.Module`.
        # - Parameter source: The source of the Pkl module.
        config = pkl.load(source, parser=pkl.Parser(namespace=globals()))
        return config
