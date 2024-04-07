# Code generated from Pkl module `Foo`. DO NOT EDIT.
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, Set, Union

import pkl


@dataclass
class Being:
    exists: bool

    _registered_identifier = "Foo#Being"


@dataclass
class Animal(Being):
    name: str

    _registered_identifier = "Foo#Animal"


@dataclass
class Dog(Animal):
    barks: bool

    _registered_identifier = "Foo#Dog"


@dataclass
class Bird(Animal):
    flies: bool

    _registered_identifier = "Foo#Bird"


@dataclass
class Foo:
    animals: List[Animal]

    _registered_identifier = "Foo"

    @classmethod
    def load_pkl(cls, source):
        # Load the Pkl module at the given source and evaluate it into `Foo.Module`.
        # - Parameter source: The source of the Pkl module.
        config = pkl.load(source, parser=pkl.Parser(namespace=globals()))
        return config
