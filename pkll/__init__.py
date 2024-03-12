import os
from typing import Dict, List, Optional

from pkll.evaluator import EVALUATOR_DEFAULT, Evaluator
from pkll.msgapi.outgoing import ClientModuleReader, ClientResourceReader, Project
from pkll.server import PKLServer

# get version
with open(os.path.join(os.path.dirname(__file__), "VERSION"), "r") as _f:
    __version__ = _f.read().strip()


def load(
    moduleUri: str,
    moduleText: Optional[str] = None,
    expr: Optional[str] = None,
    *,
    force_render=False,
    parser=None,
    allowedModules: Optional[List[str]] = [
        "pkl:",
        "file:",
        "modulepath:",
        "https:",
        "repl:",
        "package:",
        "projectpackage:",
    ],
    allowedResources: Optional[List[str]] = [
        "env:",
        "prop:",
        "package:",
        "projectpackage:",
    ],
    clientModuleReaders: Optional[List[ClientModuleReader]] = None,
    clientResourceReaders: Optional[List[ClientResourceReader]] = None,
    modulePaths: Optional[List[str]] = None,
    env: Optional[Dict[str, str]] = EVALUATOR_DEFAULT,
    properties: Optional[Dict[str, str]] = None,
    timeoutSeconds: Optional[int] = None,
    rootDir: Optional[str] = None,
    cacheDir: Optional[str] = EVALUATOR_DEFAULT,
    outputFormat: Optional[str] = None,
    project: Optional[Project] = None,
    module_handler=None,
    resource_handler=None,
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
        force_render (bool, False): Force the rendering of the module,
            even if it might not be necessary under normal circumstances.
        parser: A specific parser to be used for parsing the module.
            If None, a default parser is used.
        allowedModules (Optional[List[str]]): List of URI schemes that are allowed
            for module imports, with default schemes provided.
        allowedResources (Optional[List[str]]): List of URI schemes that are allowed
            for resource reading, with default schemes provided.
        clientModuleReaders (Optional[List[ClientModuleReader]]): Custom module readers
            for handling specific URI schemes on the client side.
        clientResourceReaders (Optional[List[ClientResourceReader]]): Custom resource
            readers for handling specific URI schemes on the client side.
        modulePaths (Optional[List[str]]): Additional paths to search when resolving module URIs.
        env (Optional[Dict[str, str]], EVALUATOR_DEFAULT): Environment variables to set
            for the evaluation process.
        properties (Optional[Dict[str, str]], None): External properties to set
            for the evaluation process.
        timeoutSeconds (Optional[int], None): Maximum duration in seconds
            for the evaluation to complete.
        rootDir (Optional[str], None): Restrict file-based module and resource access
            to within this root directory.
        cacheDir (Optional[str], EVALUATOR_DEFAULT): Directory to use for caching packages.
        outputFormat (Optional[str], None): Desired output format for the evaluation result.
        project (Optional[Project], None): Project dependencies and settings for the evaluation.
        module_handler: Custom handler for module loading and evaluation processes.
        resource_handler: Custom handler for resource loading processes.
        debug (bool, False): Enable debugging mode for additional output and diagnostics.
        **kwargs: Additional keyword arguments for extensibility and future use.

    Returns:
        The result of the module or expression evaluation, depending on the inputs and configuration.

    This function provides a flexible interface for loading and evaluating Pkl modules
    with a variety of customization options, including custom module and resource readers,
    environmental configurations, and support for complex project dependencies.
    """
    with Evaluator(
        allowedModules=allowedModules,
        allowedResources=allowedResources,
        clientModuleReaders=clientModuleReaders,
        clientResourceReaders=clientResourceReaders,
        modulePaths=modulePaths,
        env=env,
        properties=properties,
        timeoutSeconds=timeoutSeconds,
        rootDir=rootDir,
        cacheDir=cacheDir,
        outputFormat=outputFormat,
        project=project,
        debug=debug,
        **kwargs,
    ) as evaluator:
        return evaluator.request(
            moduleUri,
            moduleText,
            expr,
            force_render=force_render,
            parser=parser,
            module_handler=module_handler,
            resource_handler=resource_handler,
        )


__all__ = ["load", "Evaluator", "PKLServer"]
