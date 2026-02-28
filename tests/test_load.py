import pkl


def test_load():
    _ = pkl.load("./tests/pkls/types.pkl")


def test_loads():
    config = pkl.loads("a: Int = 1 + 1")
    assert config.a == 2


def test_load_expr():
    config = pkl.load("./tests/pkls/types.pkl", expr="datasize")
    assert config.__class__.__name__ == "DataSize"


def test_load_text():
    config = pkl.load(None, module_text="a: Int = 1 + 1")
    assert config.a == 2


def test_load_debug():
    _ = pkl.load("./tests/pkls/types.pkl", debug=True)


def test_multiple_dynamic_shapes():
    """Regression for https://github.com/jw-y/pkl-python/issues/11.
    Two Dynamic values with different members must not share a cached dataclass.
    """
    config = pkl.loads("""
dynamic1 {
    a = "a"
}
dynamic2 {
    b = "b"
    c = "c"
}
""")
    assert config.dynamic1.a == "a"
    assert config.dynamic2.b == "b"
    assert config.dynamic2.c == "c"
