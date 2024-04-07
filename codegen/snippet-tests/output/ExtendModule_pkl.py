# Code generated from Pkl module `ExtendModule`. DO NOT EDIT.
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, Set, Union

import pkl

from . import MyModule_pkl


@dataclass
class ExtendModule(MyModule_pkl.MyModule):
    bar: str

    _registered_identifier = "ExtendModule"

    @classmethod
    def load_pkl(cls, source):
        # Load the Pkl module at the given source and evaluate it into `ExtendModule.Module`.
        # - Parameter source: The source of the Pkl module.
        config = pkl.load(source, parser=pkl.Parser(namespace=globals()))
        return config
