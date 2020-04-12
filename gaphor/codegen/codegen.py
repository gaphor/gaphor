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
    parser.add_argument("modelfile", type=Path, help="gaphor model filename")
    parser.add_argument("outfile", type=Path, help="python data model filename")
    parser.add_argument("overrides", type=Path, help="override filename")
    args = parser.parse_args()
    print(f"Generating {args.outfile} from {args.modelfile}...")
    print("  (warnings can be ignored)")

    autocoder.generate(args.modelfile, args.outfile, args.overrides)
    byte_compile([str(args.outfile)])


if __name__ == "__main__":
    main()
