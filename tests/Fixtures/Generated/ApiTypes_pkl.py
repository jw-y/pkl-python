# Code generated from Pkl module `ApiTypes`. DO NOT EDIT.
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, Set, Union

import pkl


@dataclass
class ApiTypes:
    res1: pkl.Pair[int, str]

    res2: pkl.Duration

    res3: pkl.DataSize

    _registered_identifier = "ApiTypes"

    @classmethod
    def load_pkl(cls, source):
        # Load the Pkl module at the given source and evaluate it into `ApiTypes.Module`.
        # - Parameter source: The source of the Pkl module.
        config = pkl.load(source, namespace=globals())
        return config
