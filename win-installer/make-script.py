import sys

import tomlkit


def main(toml_file):
    with open(toml_file) as f:
        toml = tomlkit.parse(f.read())

    plugins = toml["tool"]["poetry"]["plugins"]
    for cat in plugins.values():
        for entrypoint in cat.values():
            print(f"import {entrypoint.split(':')[0]}")

    print("from gaphor.ui import main")
    print("import sys")
    print("main(sys.argv)")


if __name__ == "__main__":
    main(sys.argv[1])
