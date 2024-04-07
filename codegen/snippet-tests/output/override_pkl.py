# Code generated from Pkl module `override`. DO NOT EDIT.
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, Set, Union

import pkl


@dataclass
class Foo:
    myProp: str

    _registered_identifier = "override#Foo"


@dataclass
class Bar(Foo):
    myProp: str

    _registered_identifier = "override#Bar"


@dataclass
class override:
    foo: Foo

    _registered_identifier = "override"

    @classmethod
    def load_pkl(cls, source):
        # Load the Pkl module at the given source and evaluate it into `override.Module`.
        # - Parameter source: The source of the Pkl module.
        config = pkl.load(source, parser=pkl.Parser(namespace=globals()))
        return config
