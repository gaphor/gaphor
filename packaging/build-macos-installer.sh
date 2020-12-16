#!/usr/bin/env bash

set -euo pipefail

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "${DIR}"
mkdir -p output

VERSION="$(poetry version --no-ansi | cut -d' ' -f2)"
YEAR="$(python -c "from datetime import date;print(date.today().year)")"

python -m venv pyinstvenv

pyinstvenv/bin/pip install "../dist/gaphor-${VERSION}-py3-none-any.whl"
pyinstvenv/bin/pip install pyinstaller==4.1.0

sed "s/__version__/$VERSION/g" "${DIR}"/file_version_info.txt.in > "${DIR}"/file_version_info.txt
sed "s/__version__/$VERSION/g;s/__year__/$YEAR/g" "${DIR}"/gaphor.spec.in > "${DIR}"/gaphor.spec
python make-script.py ../pyproject.toml > gaphor-script.py
pyinstvenv/bin/pyinstaller -y gaphor.spec
python fix-folder-names-for-codesign.py "${DIR}"/dist/Gaphor-"${VERSION}".app

rm -rf pyinstvenv
echo 'Done!'
