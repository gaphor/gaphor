#!/bin/bash

echo "GITHUB_REF is $GITHUB_REF"
TAG="${GITHUB_REF/refs\/tags\//}"
echo "TAG is $TAG"
if ! [ -x "$(command -v poetry)" ]; then
    echo 'Poetry not found, activating venv'
    source venv
fi
VERSION="$(poetry version --no-ansi | cut -d' ' -f2)"
echo "VERSION is $VERSION"

if [[ "$GITHUB_REF" =~ refs\/tags\/.* && "$TAG" == "$VERSION" ]]
then
    REV=""
    RELEASE="true"
else
    REV=".dev0+${GITHUB_SHA:0:8}"
    RELEASE="false"

    # Update version, so it will also show in the Gaphor application
    poetry version "${VERSION}""${REV}"
fi

echo "::set-output name=version::${VERSION}${REV}"
echo "::set-output name=release::${RELEASE}"
