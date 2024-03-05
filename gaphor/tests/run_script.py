# ruff: noqa: T201

from gaphor.application import distribution

if __name__ == "__main__":
    print("Running a test script for Gaphor", distribution().version)
