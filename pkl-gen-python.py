import argparse
import os
import sys
import tempfile
from dataclasses import replace
from pathlib import Path

from black import FileMode, format_str
import isort

import pkl


def format_code(code: str, line_length: int = 88) -> str:

    try:
        code = isort.code(code)
        # Format the code using Black's format_str function
        formatted_code = format_str(code, mode=FileMode(line_length=line_length))
        return formatted_code
    except Exception as e:
        # Handle potential errors, e.g., syntax errors in the input code
        print(f"Error formatting code: {e}")
        return code  # Return the original code if formatting fails


class GeneratorSettings:
    EMPTY = {
        "inputs": [],
        "output_path": None,
        "dry_run": None,
        "generate_script": None,
    }


def run_inner(settings, pkl_input_module, verbose=False):
    output_path = Path(settings.outputPath or "./.out")

    gen_script_path = Path(settings.generateScript).absolute()

    module_to_evaluate = f"""\
    amends "{gen_script_path}"

    import "{pkl_input_module}" as theModule

    moduleToGenerate = theModule\
    """
    with tempfile.NamedTemporaryFile("w+t", suffix=".pkl") as temp_file:
        temp_file.write(module_to_evaluate)
        temp_file.flush()
        if verbose:
            print("temp_file:", temp_file.name)

        tmp_uri = Path(temp_file.name).as_uri()
        files = pkl.load(
            tmp_uri, expr="output.files.toMap().mapValues((_, it) -> it.text)"
        )

    if verbose:
        for f in files.values():
            print(f)

    for filename, contents in files.items():
        fp = output_path / filename
        if settings.dryRun:
            print("DRYRUN:", fp)
            continue
        else:
            print("Written to:", fp)
        fp.parent.mkdir(exist_ok=True)
        with open(fp, "w", encoding="utf-8") as file:
            contents = format_code(contents)
            file.write(contents)


def run_modules(settings):
    for pkl_input_module in settings.inputs:
        run_inner(settings, pkl_input_module)


def load_generator_settings(settings_file=None):
    if settings_file is None and os.path.exists("generator-settings.pkl"):
        settings_file = "generator-settings.pkl"
    if settings_file is None:
        return GeneratorSettings.EMPTY
    # config = pkl.load(Path(settings_file).absolute().as_uri())
    config = pkl.load(settings_file)
    return config


def build_generator_settings(args, pkl_input_modules):
    generator_settings = load_generator_settings(args.generator_settings)
    if pkl_input_modules:
        generator_settings = replace(generator_settings, inputs=pkl_input_modules)
    if args.dry_run:
        generator_settings = replace(generator_settings, dryRun=args.dry_run)
    if args.output_path:
        generator_settings = replace(generator_settings, outputPath=args.output_path)

    if generator_settings.generateScript is None:
        raise ValueError("generateScript not specified")
    return generator_settings


def main():
    parser = argparse.ArgumentParser(description="PklGenSwift Command-Line Tool")
    # parser.add_argument('--generate-script', type=str,
    #        help='Path to the generate script (hidden option)', default=None)
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
        "pkl_input_modules", nargs="+", help="The Pkl modules to generate as Python"
    )
    args = parser.parse_args()

    if args.version:
        print(pkl.__version__)
        sys.exit()

    pkl_input_modules = [Path(module).absolute() for module in args.pkl_input_modules]
    settings = build_generator_settings(args, pkl_input_modules)

    if settings.dryRun:
        print("Running in dry-run mode", file=sys.stderr)

    for pkl_input_module in settings.inputs:
        run_inner(settings, pkl_input_module, verbose=args.verbose)

    print("Generation complete.")


if __name__ == "__main__":
    main()
