import os
from pathlib import Path
from typing import Optional, Union
from urllib.parse import ParseResult, urlparse

from pkl.evaluator_manager import Evaluator, EvaluatorManager
from pkl.evaluator_options import EvaluatorOptions, PreconfiguredOptions
from pkl.parser import DataSize, Duration, IntSeq, Pair, Parser, Regex
from pkl.reader import ModuleReader, PathElement, ResourceReader
from pkl.utils import ModuleSource, PklBugError, PklError

# get version
with open(os.path.join(os.path.dirname(__file__), "VERSION"), "r") as _f:
    __version__ = _f.read().strip()


class PklDefaultType:
    def __repr__(self):
        return "<PklDefault>"


PKL_DEFAULT = PklDefaultType()


def _search_project_dir(module_path: str) -> str:
    cur_path = Path(module_path).parent.absolute()
    while not (cur_path / "PklProject").exists():
        cur_path = cur_path.parent
        if str(cur_path) == "/":
            break

    if str(cur_path) == "/":
        cur_path = Path(module_path).parent
    return str(cur_path.absolute())


def load(
    module_uri: Union[str, Path],
    *,
    module_text: Optional[str] = None,
    expr: Optional[str] = None,
    project_dir: str = PKL_DEFAULT,
    evaluator_options: EvaluatorOptions = PreconfiguredOptions(),
    parser=None,
    debug=False,
    **kwargs,
):
    """
    Loads and evaluates a Pkl module or expression with specified parameters and customization options.

    Args:
        module_uri (str): The absolute URI of the module to be loaded.
        module_text (Optional[str], None): Optionally, the content of the module to be loaded.
            If None, the module is loaded from the specified URI.
        expr (Optional[str], None): Optionally, a Pkl expression to be evaluated
            within the loaded module. If None, the entire module is evaluated.
        project_dir (str, PKL_DEFAULT): The project directory to use for this command.
            By default, searches up from the working directory for a PklProject file.
        evaluator_options (EvaluatorOptions, PreconfiguredOptions()):
            extra options for evaluator
        parser: A specific parser to be used for parsing the module.
            If None, a default parser is used.
        debug (bool, False): Enable debugging mode for additional output and diagnostics.
        **kwargs: Additional keyword arguments for extensibility and future use.

    Returns:
        The result of the module or expression evaluation, depending on the inputs and configuration.

    This function provides a flexible interface for loading and evaluating Pkl modules
    with a variety of customization options, including custom module and resource readers,
    environmental configurations, and support for complex project dependencies.
    """

    parsed = urlparse(str(module_uri))

    def is_uri(_uri: ParseResult):
        return bool(_uri.scheme) and (bool(_uri.netloc) or bool(_uri.path))

    if module_text:
        source = ModuleSource.from_text(module_text)
    elif is_uri(parsed):
        source = ModuleSource.from_uri(module_uri)
    else:
        source = ModuleSource.from_path(module_uri)

    if project_dir is PKL_DEFAULT:
        project_dir = _search_project_dir(str(module_uri))

    with EvaluatorManager(debug=debug) as manager:
        if (Path(project_dir) / "PklProject").exists():
            evaluator = manager.new_project_evaluator(
                project_dir, evaluator_options, parser=parser
            )
        else:
            evaluator = manager.new_evaluator(evaluator_options, parser=parser)
        config = evaluator.evaluate_expression(source, expr)
    return config


__all__ = [
    "load",
    "Evaluator",
    "EvaluatorManager",
    "EvaluatorOptions",
    "PreconfiguredOptions",
    "ModuleReader",
    "ResourceReader",
    "PathElement",
    "Parser",
    "ModuleSource",
    "PklError",
    "PklBugError",
    "Duration",
    "DataSize",
    "Pair",
    "IntSeq",
    "Regex",
]
