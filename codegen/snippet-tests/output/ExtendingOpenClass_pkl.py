# Code generated from Pkl module `ExtendingOpenClass`. DO NOT EDIT.
from __future__ import annotations
from typing import Any, Dict, List, Literal, Optional, Set, Union
from dataclasses import dataclass
import pkl
from . import lib3_pkl


@dataclass
class MyClass2(lib3_pkl.GoGoGo):
    myBoolean: bool

    _registered_identifier = "ExtendingOpenClass#MyClass2"

@dataclass
class MyOpenClass:
    myStr: str

    _registered_identifier = "ExtendingOpenClass#MyOpenClass"

@dataclass
class MyClass(MyOpenClass):
    myStr: str

    myBoolean: bool

    _registered_identifier = "ExtendingOpenClass#MyClass"

@dataclass
class ModuleClass:
    res1: MyClass

    res2: MyClass2

    _registered_identifier = "ExtendingOpenClass"

    @classmethod
    def load_pkl(cls, source):
        # Load the Pkl module at the given source and evaluate it into `ExtendingOpenClass.Module`.
        # - Parameter source: The source of the Pkl module.
        config = pkl.load(source, parser=pkl.Parser(namespace = globals()))
        return config