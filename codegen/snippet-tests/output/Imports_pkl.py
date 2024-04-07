# Code generated from Pkl module `Imports`. DO NOT EDIT.
from __future__ import annotations
from typing import Any, Dict, List, Literal, Optional, Set, Union
from dataclasses import dataclass
import pkl
from . import Foo_pkl


@dataclass
class ModuleClass:
    foo: Foo_pkl.ModuleClass

    _registered_identifier = "Imports"

    @classmethod
    def load_pkl(cls, source):
        # Load the Pkl module at the given source and evaluate it into `Imports.Module`.
        # - Parameter source: The source of the Pkl module.
        config = pkl.load(source, parser=pkl.Parser(namespace = globals()))
        return config