# Code generated from Pkl module `union`. DO NOT EDIT.
from __future__ import annotations
from typing import Any, Dict, List, Literal, Optional, Set, Union
from dataclasses import dataclass
import pkl


City = Literal["San Francisco", "London", "上海"]

County = Literal["San Francisco", "San Mateo", "Yolo"]

Noodles = Literal["拉面", "刀切面", "面线", "意大利面"]

AccountDisposition = Literal["", "icloud3", "prod", "shared"]

@dataclass
class ModuleClass:
    # A city
    city: City

    # County
    county: County

    # Noodles
    noodle: Noodles

    # Account disposition
    disposition: AccountDisposition

    _registered_identifier = "union"

    @classmethod
    def load_pkl(cls, source):
        # Load the Pkl module at the given source and evaluate it into `union.Module`.
        # - Parameter source: The source of the Pkl module.
        config = pkl.load(source, parser=pkl.Parser(namespace = globals()))
        return config