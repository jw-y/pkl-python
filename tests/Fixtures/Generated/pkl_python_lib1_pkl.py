# Code generated from Pkl module `pkl.python.lib1`. DO NOT EDIT.
from __future__ import annotations

from dataclasses import dataclass

import pkl


@dataclass
class Being:
    exists: bool

    _registered_identifier = "pkl.python.lib1#Being"


@dataclass
class lib1:
    _registered_identifier = "pkl.python.lib1"

    @classmethod
    def load_pkl(cls, source):
        # Load the Pkl module at the given source and evaluate it into `pkl_python_lib1.Module`.
        # - Parameter source: The source of the Pkl module.
        config = pkl.load(source, parser=pkl.Parser(namespace=globals()))
        return config
