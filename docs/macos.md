# Gaphor on macOS

## Development Environment

To setup a development environment with macOS:
1. Install [homebrew](https://brew.sh)
1. Open a terminal and execute:
```bash
$ brew install python3 gobject-introspection gtk+3
```
[Clone the repository](https://help.github.com/en/articles/cloning-a-repository).
```
$ cd gaphor
$ source ./venv
$ poetry run gaphor
```

## Packaging for macOS

In order to create a dmg package for macOS, we utilize a custom bash script
that picks up the required files, drops them in a bundle, and changes the
link references.

1. Follow the instructions for settings up a development environment above
1. Open a terminal and execute the following from the repository directory:
```bash
$ cd macos-dmg
$ source package.sh
```
