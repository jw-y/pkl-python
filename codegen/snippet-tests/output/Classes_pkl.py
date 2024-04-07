# Code generated from Pkl module `Classes`. DO NOT EDIT.
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, Set, Union

import pkl


@dataclass
class Animal:
    name: str

    _registered_identifier = "Classes#Animal"


@dataclass
class Classes:
    animals: List[Animal]

    _registered_identifier = "Classes"

    @classmethod
    def load_pkl(cls, source):
        # Load the Pkl module at the given source and evaluate it into `Classes.Module`.
        # - Parameter source: The source of the Pkl module.
        config = pkl.load(source, parser=pkl.Parser(namespace=globals()))
        return config
