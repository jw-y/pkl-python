# Code generated from Pkl module `Collections`. DO NOT EDIT.
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, Set, Union

import pkl


@dataclass
class Collections:
    res1: List[int]

    res2: List[int]

    res3: List[List[int]]

    res4: List[List[int]]

    res5: Dict[int, bool]

    res6: Dict[int, Dict[int, bool]]

    res7: Dict[int, bool]

    res8: Dict[int, Dict[int, bool]]

    res9: Set[str]

    res10: Set[int]

    _registered_identifier = "Collections"

    @classmethod
    def load_pkl(cls, source):
        # Load the Pkl module at the given source and evaluate it into `Collections.Module`.
        # - Parameter source: The source of the Pkl module.
        config = pkl.load(source, namespace=globals())
        return config
