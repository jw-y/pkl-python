# Code generated from Pkl module `Enums`. DO NOT EDIT.
from __future__ import annotations
from typing import Any, Dict, List, Literal, Optional, Set, Union
from dataclasses import dataclass
import pkl


City = Literal["San Francisco", "London", "Zurich", "Cupertino"]

Animal = Union["Horse", "Zebra", "Monkey"]

DictOrArray = Union[Dict[str, str], List[str]]

BugBug = Literal["bug bug", "bugBug"]

HorseOrBug = Union["Horse", Literal["bug bug", "bugBug"]]

MaybeHorseOrDefinitelyZebra = Union[Optional["Horse"], "Zebra"]

@dataclass
class Monkey:
    tail: str

    _registered_identifier = "Enums#Monkey"

@dataclass
class Zebra:
    stripes: str

    _registered_identifier = "Enums#Zebra"

@dataclass
class Horse:
    neigh: bool

    _registered_identifier = "Enums#Horse"

@dataclass
class ModuleClass:
    # City of tomorrow!
    city: City

    # The animal
    animal: Animal

    # Some dictionary or array type.
    dictOrArray: DictOrArray

    # Bugs are cool.
    bug: BugBug

    horseOrBug: HorseOrBug

    _registered_identifier = "Enums"

    @classmethod
    def load_pkl(cls, source):
        # Load the Pkl module at the given source and evaluate it into `Enums.Module`.
        # - Parameter source: The source of the Pkl module.
        config = pkl.load(source, parser=pkl.Parser(namespace = globals()))
        return config