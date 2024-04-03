import pkl


def test_load():
    _ = pkl.load("./tests/types.pkl")


def test_load_expr():
    config = pkl.load("./tests/types.pkl", expr="datasize")
    assert config.__class__.__name__ == "DataSize"


def test_load_text():
    config = pkl.load(None, module_text="a: Int = 1 + 1")
    assert config.a == 2


def test_load_debug():
    _ = pkl.load("./tests/types.pkl", debug=True)
