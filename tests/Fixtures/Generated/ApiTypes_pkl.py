# Code generated from Pkl module `ApiTypes`. DO NOT EDIT.
from __future__ import annotations
from typing import Any, Dict, List, Literal, Optional, Set, Union
from dataclasses import dataclass
import pkl


@dataclass
class ModuleClass:
    res1: Pair[int, str]

    res2: Duration

    res3: DataSize

    _registered_identifier = "ApiTypes"

    @classmethod
    def load_pkl(cls, source):
        # Load the Pkl module at the given source and evaluate it into `ApiTypes.Module`.
        # - Parameter source: The source of the Pkl module.
        config = pkl.load(source, parser=pkl.Parser(namespace = globals()))
        return config