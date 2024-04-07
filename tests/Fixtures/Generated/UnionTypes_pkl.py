# Code generated from Pkl module `UnionTypes`. DO NOT EDIT.
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Union

import pkl

Fruit = Union["Banana", "Grape", "Apple"]


City = Literal["San Francisco", "Tokyo", "Zurich", "London"]


ZebraOrDonkey = Union["Zebra", "Donkey"]


AnimalOrString = Union["Animal", str]


@dataclass
class Animal:
    name: str

    _registered_identifier = "UnionTypes#Animal"


@dataclass
class Donkey(Animal):
    name: str

    _registered_identifier = "UnionTypes#Donkey"


@dataclass
class Zebra(Animal):
    name: str

    _registered_identifier = "UnionTypes#Zebra"


@dataclass
class Apple:
    isRed: bool

    _registered_identifier = "UnionTypes#Apple"


@dataclass
class Grape:
    isUsedForWine: bool

    _registered_identifier = "UnionTypes#Grape"


@dataclass
class Banana:
    isRipe: bool

    _registered_identifier = "UnionTypes#Banana"


@dataclass
class UnionTypes:
    fruit1: Fruit

    fruit2: Fruit

    fruit3: Fruit

    city1: City

    city2: City

    city3: City

    city4: City

    animal1: ZebraOrDonkey

    animal2: ZebraOrDonkey

    animalOrString1: AnimalOrString

    animalOrString2: AnimalOrString

    _registered_identifier = "UnionTypes"

    @classmethod
    def load_pkl(cls, source):
        # Load the Pkl module at the given source and evaluate it into `UnionTypes.Module`.
        # - Parameter source: The source of the Pkl module.
        config = pkl.load(source, parser=pkl.Parser(namespace=globals()))
        return config
