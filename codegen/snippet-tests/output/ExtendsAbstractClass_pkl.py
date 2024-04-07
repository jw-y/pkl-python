# Code generated from Pkl module `ExtendsAbstractClass`. DO NOT EDIT.
from __future__ import annotations
from typing import Any, Dict, List, Literal, Optional, Set, Union
from dataclasses import dataclass
import pkl


@dataclass
class A:
    b: str

    _registered_identifier = "ExtendsAbstractClass#A"

@dataclass
class B(A):
    b: str

    c: str

    _registered_identifier = "ExtendsAbstractClass#B"

@dataclass
class ModuleClass:
    a: A

    _registered_identifier = "ExtendsAbstractClass"

    @classmethod
    def load_pkl(cls, source):
        # Load the Pkl module at the given source and evaluate it into `ExtendsAbstractClass.Module`.
        # - Parameter source: The source of the Pkl module.
        config = pkl.load(source, parser=pkl.Parser(namespace = globals()))
        return config