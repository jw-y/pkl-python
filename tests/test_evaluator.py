from pkl import Evaluator


def test_evaluator():
    evaluator = Evaluator()
    evaluator.create()
    evaluator.close()
