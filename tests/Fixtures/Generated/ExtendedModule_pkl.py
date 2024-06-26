# Code generated from Pkl module `ExtendedModule`. DO NOT EDIT.
from __future__ import annotations

from dataclasses import dataclass

import pkl

from . import OpenModule_pkl


@dataclass
class ExtendedModule(OpenModule_pkl.OpenModule):
    foo: str

    bar: int

    _registered_identifier = "ExtendedModule"

    @classmethod
    def load_pkl(cls, source):
        # Load the Pkl module at the given source and evaluate it into `ExtendedModule.Module`.
        # - Parameter source: The source of the Pkl module.
        config = pkl.load(source, parser=pkl.Parser(namespace=globals()))
        return config
