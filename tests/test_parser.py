from pathlib import Path

import pytest

import pkl

base_path = Path("./tests/Fixtures")


def test_AnyType():
    file = base_path / "AnyType.pkl"
    _ = pkl.load(file)


def test_ApiTypes():
    file = base_path / "ApiTypes.pkl"
    _ = pkl.load(file)


def test_Classes():
    file = base_path / "Classes.pkl"
    _ = pkl.load(file)


def test_Collections():
    file = base_path / "Collections.pkl"
    _ = pkl.load(file)


def test_ExtendedModule():
    file = base_path / "ExtendedModule.pkl"
    _ = pkl.load(file)


def test_OpenModule():
    file = base_path / "OpenModule.pkl"
    with pytest.raises(Exception):
        _ = pkl.load(file)


def test_Poly():
    file = base_path / "Poly.pkl"
    _ = pkl.load(file)


def test_UnionTypes():
    file = base_path / "UnionTypes.pkl"
    _ = pkl.load(file)


def test_lib1():
    file = base_path / "lib1.pkl"
    _ = pkl.load(file)


def test_types():
    file = Path("./tests") / "types.pkl"
    _ = pkl.load(file)
