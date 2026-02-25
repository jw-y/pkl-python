import argparse
import sys
import tempfile
import warnings
from dataclasses import dataclass, replace
from pathlib import Path
from typing import List, Optional
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
