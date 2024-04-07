# Code generated from Pkl module `AnyType`. DO NOT EDIT.
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pkl


@dataclass
class Bird:
    species: str

    _registered_identifier = "AnyType#Bird"


@dataclass
class AnyType:
    bird: Any

    primitive: Any

    primitive2: Any

    array: Any

    set: Any

    mapping: Any

    nullable: Any

    duration: Any

    dataSize: Any

    _registered_identifier = "AnyType"

    @classmethod
    def load_pkl(cls, source):
        # Load the Pkl module at the given source and evaluate it into `AnyType.Module`.
        # - Parameter source: The source of the Pkl module.
        config = pkl.load(source, parser=pkl.Parser(namespace=globals()))
        return config
