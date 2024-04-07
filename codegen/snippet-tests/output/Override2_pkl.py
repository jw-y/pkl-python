# Code generated from Pkl module `Override2`. DO NOT EDIT.
from __future__ import annotations
from typing import Any, Dict, List, Literal, Optional, Set, Union
from dataclasses import dataclass
import pkl


@dataclass
class ModuleClass:
    # Doc comments
    foo: str

    _registered_identifier = "Override2"

@dataclass
class MySubclass(ModuleClass):
    # Different doc comments
    foo: str

    _registered_identifier = "Override2#MySubclass"

    @classmethod
    def load_pkl(cls, source):
        # Load the Pkl module at the given source and evaluate it into `Override2.Module`.
        # - Parameter source: The source of the Pkl module.
        config = pkl.load(source, parser=pkl.Parser(namespace = globals()))
        return config