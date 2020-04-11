#!/usr/bin/env python
"""The Gaphor code generator CLI.

Provides the CLI for the code generator which transforms a Gaphor models (with
.gaphor file extension) in to a data model in Python.
"""

import argparse
from distutils.util import byte_compile
from pathlib import Path

from gaphor.codegen import autocoder


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("model_name", type=str, help="gaphor model name stem")
    parser.add_argument("--no-overrides", action="store_true", help="no overrides file")
    parser.add_argument(
        "--model_dir",
        type=Path,
        default=Path(__file__).absolute().parent.parent.parent / "models",
        help="optional, path to the model directory, defaults to the models " "package",
    )
    parser.add_argument(
        "--output_dir",
        type=Path,
        help="optional, path to the output direction, defaults to the "
        "model_name package",
    )
    args = parser.parse_args()
    model: str = args.model_name
    model_file: Path = args.model_dir / f"{model}.gaphor"

    if args.no_overrides:
        overrides = None
    else:
        overrides = args.model_dir / f"{args.model_name}.override"

    if args.output_dir:
        outfile = args.output_dir / f"{model.lower()}.py"
    elif model == "Core":
        outfile = Path(__file__).absolute().parent.parent / "core/modeling/coremodel.py"
    else:
        outfile = (
            Path(__file__).absolute().parent.parent / model / f"{model.lower()}.py"
        )

    print(f"Generating {outfile.name} from {model}.gaphor...")
    print("  (warnings can be ignored)")

    autocoder.generate(model_file, outfile, overrides)
    byte_compile([str(outfile)])


if __name__ == "__main__":
    main()
