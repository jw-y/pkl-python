from pathlib import Path

import pkl
from tests.Fixtures.Generated.AnyType_pkl import AnyType, Bird
from tests.Fixtures.Generated.ApiTypes_pkl import ApiTypes
from tests.Fixtures.Generated.Classes_pkl import Animal, Classes
from tests.Fixtures.Generated.Collections_pkl import Collections
from tests.Fixtures.Generated.ExtendedModule_pkl import ExtendedModule

base_path = Path("./tests/Fixtures")


def test_evaluate_classes():
    result = Classes.load_pkl(base_path / "Classes.pkl")
    expected = Classes(
        animals=[
            Animal(name="Uni"),
            Animal(name="Wally"),
            Animal(name="Mouse"),
        ]
    )
    assert result == expected


def test_evaluate_collections():
    result = Collections.load_pkl(base_path / "Collections.pkl")
    expected = Collections(
        res1=[1, 2, 3],
        res2=[2, 3, 4],
        res3=[[1], [2], [3]],
        res4=[[1], [2], [3]],
        res5={1: True, 2: False},
        res6={1: {1: True}, 2: {2: True}, 3: {3: True}},
        res7={1: True, 2: False},
        res8={1: {1: True}, 2: {2: False}},
        res9={"one", "two", "three"},
        res10={1, 2, 3},
    )
    assert result == expected


def test_evaluate_api_types():
    result = ApiTypes.load_pkl(base_path / "ApiTypes.pkl")
    # Define expected result based on your ApiTypes.Module structure
    expected = ApiTypes(
        res1=pkl.Pair(42, "Hello"),
        res2=pkl.Duration(10, "h"),
        res3=pkl.DataSize(1.2345, "gib"),
    )
    assert result == expected


def test_polymorphic_types():
    from tests.Fixtures.Generated.pkl_python_example_Poly_pkl import (
        Animal,
        Bird,
        Dog,
        Poly,
    )

    result = Poly.load_pkl(base_path / "Poly.pkl")
    expected = Poly(
        beings=[
            Animal(name="Lion", exists=True),
            Dog(barks=True, hates=None, name="Ruuf", exists=True),
            Bird(name="Duck", flies=False, exists=False),
        ],
        rex=Dog(barks=False, hates=None, name="Rex", exists=True),
        moreBeings={
            "duck": Bird(name="Ducky", flies=True, exists=True),
            "dog": Dog(
                barks=False,
                hates=Dog(barks=False, hates=None, name="Rex", exists=True),
                name="TRex",
                exists=True,
            ),
        },
    )
    assert result == expected


def test_polymorphic_modules():
    result = ExtendedModule.load_pkl(base_path / "ExtendedModule.pkl")
    expected = ExtendedModule(foo="foo", bar=10)
    assert result == expected


def test_any_type():
    result = AnyType.load_pkl(base_path / "AnyType.pkl")
    expected = AnyType(
        bird=Bird(species="Owl"),
        primitive="foo",
        primitive2=12,
        array=[1, 2],
        set={5, 6},
        mapping={"1": 12, 12: "1"},
        nullable=None,
        duration=pkl.Duration(5.0, unit="min"),
        dataSize=pkl.DataSize(10.0, unit="mb"),
    )
    assert result == expected


def test_union_types():
    from tests.Fixtures.Generated.UnionTypes_pkl import (
        Apple,
        Banana,
        Donkey,
        Grape,
        UnionTypes,
        Zebra,
    )

    result = UnionTypes.load_pkl(base_path / "UnionTypes.pkl")
    expected = UnionTypes(
        fruit1=Banana(isRipe=True),
        fruit2=Grape(isUsedForWine=True),
        fruit3=Apple(isRed=False),
        city1="San Francisco",
        city2="Tokyo",
        city3="Zurich",
        city4="London",
        animal1=Zebra(name="Zebra"),
        animal2=Donkey(name="Donkey"),
        animalOrString1=Zebra(name="Zebra"),
        animalOrString2="Zebra",
    )
    assert result == expected
