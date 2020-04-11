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
    parser.add_argument(
        "modelfile",
        type=Path,
        help="gaphor model filename, default location is the "
        "models package if full filename not given.",
    )
    parser.add_argument(
        "outfile",
        type=Path,
        help="python data model filename, default location is "
        "the model name package if full filename not "
        "given.",
    )
    parser.add_argument(
        "overrides",
        type=Path,
        help="override filename, default location is the "
        "models package if full filename not given.",
    )
    args = parser.parse_args()
    modelfile: Path = args.modelfile
    outfile: Path = args.outfile
    if str(modelfile) == modelfile.name:
        modelfile = (
            Path(__file__).absolute().parent.parent.parent / "models" / modelfile
        )
    if str(outfile) == outfile.name:
        outfile = Path(__file__).absolute().parent.parent / modelfile.stem / outfile
    overrides: Path = args.overrides
    if str(overrides) == overrides.name:
        overrides = (
            Path(__file__).absolute().parent.parent.parent / "models" / overrides
        )

    print(f"Generating {args.outfile} from {args.modelfile}...")
    print("  (warnings can be ignored)")

    autocoder.generate(modelfile, outfile, overrides)
    byte_compile([str(outfile)])


if __name__ == "__main__":
    main()
