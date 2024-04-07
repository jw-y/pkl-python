# Code generated from Pkl module `TypeAliased`. DO NOT EDIT.
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, Set, Union

import pkl


StringyMap = Dict[str, str]


@dataclass
class TypeAliased:
    myMap: StringyMap

    _registered_identifier = "TypeAliased"

    @classmethod
    def load_pkl(cls, source):
        # Load the Pkl module at the given source and evaluate it into `TypeAliased.Module`.
        # - Parameter source: The source of the Pkl module.
        config = pkl.load(source, parser=pkl.Parser(namespace=globals()))
        return config
