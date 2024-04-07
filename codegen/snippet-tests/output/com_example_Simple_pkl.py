# Code generated from Pkl module `com.example.Simple`. DO NOT EDIT.
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, Set, Union

import pkl


@dataclass
class ClassWithReallyLongConstructor:
    theProperty1: str

    theProperty2: str

    theProperty3: str

    theProperty4: str

    theProperty5: str

    theProperty6: str

    _registered_identifier = "com.example.Simple#ClassWithReallyLongConstructor"


@dataclass
class OpenClassExtendingOpenClass:
    someOtherProp: Optional[bool]

    _registered_identifier = "com.example.Simple#OpenClassExtendingOpenClass"


@dataclass
class Person:
    # The name of the person
    the_name: str

    # Some name that matches a keyword
    enum: str

    _registered_identifier = "com.example.Simple#Person"


@dataclass
class ThePerson(Person):
    the: str

    _registered_identifier = "com.example.Simple#ThePerson"


@dataclass
class Simple:
    # This is truly a person.
    person: Person

    _registered_identifier = "com.example.Simple"

    @classmethod
    def load_pkl(cls, source):
        # Load the Pkl module at the given source and evaluate it into `com_example_Simple.Module`.
        # - Parameter source: The source of the Pkl module.
        config = pkl.load(source, parser=pkl.Parser(namespace=globals()))
        return config
