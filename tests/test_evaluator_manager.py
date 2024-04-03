from pkl import EvaluatorManager, EvaluatorOptions, ModuleSource, PreconfiguredOptions


def test_manager():
    with EvaluatorManager(debug=True) as manager:
        manager.new_evaluator(EvaluatorOptions())


def test_multiple():
    with EvaluatorManager(debug=True) as manager:
        opts = PreconfiguredOptions()
        evaluator = manager.new_evaluator(opts)
        source = ModuleSource.from_path("./tests/with_log.pkl")
        evaluator.evaluate_module(source)
