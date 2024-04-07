# Code generated from Pkl module `lib3`. DO NOT EDIT.
from __future__ import annotations
from typing import Any, Dict, List, Literal, Optional, Set, Union
from dataclasses import dataclass
import pkl


@dataclass
class GoGoGo:
    duck: Literal["quack"]

    _registered_identifier = "lib3#GoGoGo"

@dataclass
class ModuleClass:
    _registered_identifier = "lib3"

    @classmethod
    def load_pkl(cls, source):
        # Load the Pkl module at the given source and evaluate it into `lib3.Module`.
        # - Parameter source: The source of the Pkl module.
        config = pkl.load(source, parser=pkl.Parser(namespace = globals()))
        return config