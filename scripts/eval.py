import argparse
from pathlib import Path
from pprint import pprint

import pkll


def main(target, force=False, debug=False, is_print=False):
    target = Path(target)

    if target.is_file():
        files = [target]
    elif target.is_dir():
        files = list(target.glob("*.pkl"))
    else:
        raise ValueError(target)

    for f in files:
        if f.is_file():
            config = pkll.load(f.absolute().as_uri(), force_render=force, debug=debug)
            if is_print:
                pprint(config)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("target")
    parser.add_argument("--force", "-f", action="store_true")
    parser.add_argument("--debug", "-d", action="store_true")
    parser.add_argument("--print", "-p", action="store_true")
    args = parser.parse_args()
    main(args.target, force=args.force, debug=args.debug, is_print=args.print)
