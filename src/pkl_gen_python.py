import argparse
import ast
import sys
import tempfile
import warnings
from collections import defaultdict
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import ParseResult, urlparse

import pkl

"""
import isort
from black import FileMode, format_str

def format_code(code: str, line_length: int = 88) -> str:
    try:
        code = remove_unused(code)
        code = isort.code(code)
        # Format the code using Black's format_str function
        formatted_code = format_str(code, mode=FileMode(line_length=line_length))
        return formatted_code
    except Exception as e:
        # Handle potential errors, e.g., syntax errors in the input code
        print(f"Error formatting code: {e}")
        return code  # Return the original code if formatting fails
"""


def topological_sort(graph: Dict[str, Set[str]], all_nodes: Set[str]) -> List[str]:
    """
    Perform topological sort on a dependency graph.
    
    Args:
        graph: Dict mapping node -> set of nodes it depends on (base classes)
        all_nodes: Set of all nodes to include in the sort
    
    Returns:
        List of nodes in topologically sorted order (dependencies first)
    """
    # Calculate in-degree (number of dependencies) for each node
    in_degree = defaultdict(int)
    reverse_graph = defaultdict(set)  # node -> nodes that depend on it
    
    for node in all_nodes:
        if node not in in_degree:
            in_degree[node] = 0
    
    for node, deps in graph.items():
        for dep in deps:
            if dep in all_nodes:  # Only count dependencies within our set
                in_degree[node] += 1
                reverse_graph[dep].add(node)
    
    # Start with nodes that have no dependencies
    queue = [node for node in all_nodes if in_degree[node] == 0]
    result = []
    
    while queue:
        # Sort to ensure deterministic output
        queue.sort()
        node = queue.pop(0)
        result.append(node)
        
        for dependent in reverse_graph[node]:
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                queue.append(dependent)
    
    # If we couldn't sort all nodes, there's a cycle - return original order
    if len(result) != len(all_nodes):
        warnings.warn("Circular dependency detected in class hierarchy, keeping original order")
        return list(all_nodes)
    
    return result


def extract_class_info(code: str) -> Tuple[List[Tuple[str, int, int, Set[str]]], str, str]:
    """
    Extract class definitions from Python code.
    
    Returns:
        Tuple of:
        - List of (class_name, start_line, end_line, base_classes)
        - Code before first class
        - Code after last class (if any trailing content)
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return [], code, ""
    
    lines = code.split('\n')
    classes = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_name = node.name
            start_line = node.lineno - 1  # 0-indexed
            
            # Find end line (last line of the class body)
            end_line = start_line
            for child in ast.walk(node):
                if hasattr(child, 'lineno'):
                    end_line = max(end_line, child.lineno - 1)
                if hasattr(child, 'end_lineno') and child.end_lineno:
                    end_line = max(end_line, child.end_lineno - 1)
            
            # Extract base class names
            base_classes = set()
            for base in node.bases:
                if isinstance(base, ast.Name):
                    base_classes.add(base.id)
                elif isinstance(base, ast.Attribute):
                    # For qualified names like module.ClassName, just use the attribute
                    base_classes.add(base.attr)
            
            classes.append((class_name, start_line, end_line, base_classes))
    
    if not classes:
        return [], code, ""
    
    # Sort by start line
    classes.sort(key=lambda x: x[1])
    
    # Extract code before first class
    first_class_start = classes[0][1]
    prefix = '\n'.join(lines[:first_class_start])
    
    # Extract any trailing code after last class
    last_class_end = classes[-1][2]
    suffix = '\n'.join(lines[last_class_end + 1:]) if last_class_end + 1 < len(lines) else ""
    
    return classes, prefix, suffix


def reorder_classes(code: str) -> str:
    """
    Reorder class definitions in Python code so that base classes are defined
    before their subclasses.
    
    Args:
        code: Python source code string
        
    Returns:
        Reordered Python source code
    """
    classes, prefix, suffix = extract_class_info(code)
    
    if not classes:
        return code
    
    lines = code.split('\n')
    
    # Build dependency graph: class -> set of base classes it depends on
    class_names = {c[0] for c in classes}
    dependency_graph = {}
    class_code = {}
    
    for class_name, start_line, end_line, base_classes in classes:
        # Only track dependencies on classes defined in this file
        local_deps = base_classes & class_names
        dependency_graph[class_name] = local_deps
        # Store the code for this class (including any blank lines/decorators before it)
        class_code[class_name] = '\n'.join(lines[start_line:end_line + 1])
    
    # Topologically sort classes
    sorted_classes = topological_sort(dependency_graph, class_names)
    
    # Check if reordering is needed
    original_order = [c[0] for c in classes]
    if sorted_classes == original_order:
        return code  # No reordering needed
    
    # Rebuild the code
    reordered_parts = [prefix.rstrip()]
    
    for class_name in sorted_classes:
        if reordered_parts[-1]:  # Add blank lines between classes
            reordered_parts.append('')
            reordered_parts.append('')
        reordered_parts.append(class_code[class_name])
    
    if suffix.strip():
        reordered_parts.append('')
        reordered_parts.append(suffix)
    
    return '\n'.join(reordered_parts)


@dataclass
class GeneratorSettings:
    # The set of modules to turn into Swift code.
    #
    # A module's dependencies are also included in code generation.
    # Therefore, in most cases, it is only necessary to provide the entrypoint for code generation.
    inputs: Optional[List[str]] = None

    # The output path to write generated files into.
    #
    # Defaults to `.out`. Relative paths are resolved against the enclosing directory.
    outputPath: Optional[str] = None

    # If [true], prints the filenames that would be created, but skips writing any files.
    dryRun: Optional[bool] = None

    # The Generator.pkl script to use for code generation.
    #
    # This is an internal setting that's meant for development purposes.
    generateScript: Optional[str] = None

    _registered_identifier = "pkl.python.GeneratorSettings"

    @classmethod
    def load_pkl(cls, source):
        # Load the Pkl module at the given source and evaluate it into `GeneratorSettings.Module`.
        # - Parameter source: The source of the Pkl module.
        config = pkl.load(source, parser=pkl.Parser(namespace=globals()))
        return config


def python_generator(evaluator, settings: GeneratorSettings, pkl_input_module):
    output_path = Path(settings.outputPath or ".out")

    parsed = urlparse(str(settings.generateScript))

    def is_uri(_uri: ParseResult):
        return bool(_uri.scheme) and (bool(_uri.netloc) or bool(_uri.path))

    if is_uri(parsed):
        gen_script_path = pkl.ModuleSource.from_uri(settings.generateScript).uri
    else:
        gen_script_path = pkl.ModuleSource.from_path(settings.generateScript).uri

    pkl_input_module = Path(pkl_input_module).absolute()

    module_to_evaluate = f"""\
    amends "{gen_script_path}"

    import "{pkl_input_module}" as theModule

    moduleToGenerate = theModule\
    """

    with tempfile.NamedTemporaryFile("w+t", suffix=".pkl") as temp_file:
        temp_file.write(module_to_evaluate)
        temp_file.flush()
        source = pkl.ModuleSource.from_path(temp_file.name)
        files = evaluator.evaluate_output_files(source)

    for filename, contents in files.items():
        fp = output_path / filename
        print(fp.absolute())
        if settings.dryRun:
            continue
        fp.parent.mkdir(exist_ok=True)
        
        # Reorder classes to ensure base classes are defined before subclasses
        contents = reorder_classes(contents)
        
        with open(fp, "w", encoding="utf-8") as file:
            # contents = format_code(contents)
            file.write(contents)


def get_generator_settings_file(generator_settings_fp):
    if generator_settings_fp is not None:
        return generator_settings_fp
    default_path = Path() / "generator-settings.pkl"
    if default_path.exists():
        return default_path
    return None


def load_generator_settings(generator_settings_fp):
    settings_file = get_generator_settings_file(generator_settings_fp)
    if settings_file is None:
        return GeneratorSettings()
    config = pkl.load(settings_file)
    return config


def build_generator_settings(args):
    generator_settings = load_generator_settings(args.generator_settings)

    if args.pkl_input_modules:
        generator_settings = replace(generator_settings, inputs=args.pkl_input_modules)
    if args.output_path:
        generator_settings = replace(generator_settings, outputPath=args.output_path)

    generator_settings = replace(generator_settings, dryRun=args.dry_run)

    if generator_settings.generateScript is None:
        VERSION = pkl.__version__
        TAG = f"v{VERSION}"
        PACKAGE_PATH = (
            f"github.com/jw-y/pkl-python/releases/download/{TAG}/pkl.python@{VERSION}"
        )
        uri = f"package://{PACKAGE_PATH}#/Generator.pkl"
        generator_settings = replace(generator_settings, generateScript=uri)
    return generator_settings


def main():
    parser = argparse.ArgumentParser(description="PklGenPython Command-Line Tool")
    parser.add_argument(
        "-o",
        "--output_path",
        type=str,
        help="The output directory to write generated sources into",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the names of the files that will be generated, but don't write any files",
    )
    parser.add_argument(
        "--version", action="store_true", help="Print the version and exit"
    )
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument(
        "--generator-settings",
        type=str,
        help="The generator-settings.pkl file to use",
        default=None,
    )
    parser.add_argument(
        "pkl_input_modules", nargs="*", help="The Pkl modules to generate as Python"
    )
    args = parser.parse_args()

    if args.version:
        print(pkl.__version__)
        sys.exit()

    generator_settings = build_generator_settings(args)

    if generator_settings.dryRun:
        print("Running in dry-run mode", file=sys.stderr)

    with pkl.EvaluatorManager() as manager:
        for pkl_input_module in generator_settings.inputs or []:
            evaluator = manager.new_evaluator(pkl.PreconfiguredOptions())
            try:
                python_generator(evaluator, generator_settings, pkl_input_module)
            except pkl.PklError as e:
                warnings.warn(f"Failed to generate: {pkl_input_module}")
                warnings.warn(str(e))
                sys.exit(1)


if __name__ == "__main__":
    main()
