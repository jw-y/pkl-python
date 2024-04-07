# Code generated from Pkl module `com.example.ExtendedSimple`. DO NOT EDIT.
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, Set, Union

import pkl

from . import com_example_Simple_pkl


@dataclass
class ExtendedSimpleClass(com_example_Simple_pkl.Person):
    eyeColor: str

    _registered_identifier = "com.example.ExtendedSimple#ExtendedSimpleClass"


@dataclass
class ExtendedSimple:
    _registered_identifier = "com.example.ExtendedSimple"

    @classmethod
    def load_pkl(cls, source):
        # Load the Pkl module at the given source and evaluate it into `com_example_ExtendedSimple.Module`.
        # - Parameter source: The source of the Pkl module.
        config = pkl.load(source, parser=pkl.Parser(namespace=globals()))
        return config
