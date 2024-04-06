# Code generated from Pkl module `pkl.python.example.Poly`. DO NOT EDIT.
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, Set, Union

import pkl

from . import pkl_python_lib1_pkl


@dataclass
class Bird(pkl_python_lib1_pkl.Being):
    name: str

    flies: bool

    _registered_identifier = "pkl.python.example.Poly#Bird"


@dataclass
class Animal(pkl_python_lib1_pkl.Being):
    name: str

    _registered_identifier = "pkl.python.example.Poly#Animal"


@dataclass
class Dog(Animal):
    barks: bool

    hates: Optional[Animal]

    _registered_identifier = "pkl.python.example.Poly#Dog"


@dataclass
class Poly:
    beings: List[pkl_python_lib1_pkl.Being]

    rex: Dog

    moreBeings: Dict[str, pkl_python_lib1_pkl.Being]

    _registered_identifier = "pkl.python.example.Poly"

    @classmethod
    def load_pkl(cls, source):
        # Load the Pkl module at the given source and evaluate it into `pkl_python_example_Poly.Module`.
        # - Parameter source: The source of the Pkl module.
        config = pkl.load(source, namespace=globals())
        return config
