# Code generated from Pkl module `UnionNameKeyword`. DO NOT EDIT.
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, Set, Union

import pkl


Type = Literal["one", "two", "three"]


@dataclass
class UnionNameKeyword:
    type: Type

    _registered_identifier = "UnionNameKeyword"

    @classmethod
    def load_pkl(cls, source):
        # Load the Pkl module at the given source and evaluate it into `UnionNameKeyword.Module`.
        # - Parameter source: The source of the Pkl module.
        config = pkl.load(source, parser=pkl.Parser(namespace=globals()))
        return config
