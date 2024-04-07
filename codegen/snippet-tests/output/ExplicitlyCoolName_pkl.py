# Code generated from Pkl module `ExplicitName`. DO NOT EDIT.
from __future__ import annotations
from typing import Any, Dict, List, Literal, Optional, Set, Union
from dataclasses import dataclass
import pkl


ConfigType = Literal["one", "two"]

@dataclass
class SomethingVeryFunny:
    _registered_identifier = "ExplicitName#SomethingFunny"

@dataclass
class ModuleClass:
    MyCoolProp: SomethingVeryFunny

    _registered_identifier = "ExplicitName"

    @classmethod
    def load_pkl(cls, source):
        # Load the Pkl module at the given source and evaluate it into `ExplicitlyCoolName.Module`.
        # - Parameter source: The source of the Pkl module.
        config = pkl.load(source, parser=pkl.Parser(namespace = globals()))
        return config