#!/bin/bash

echo "GITHUB_REF is $GITHUB_REF"
TAG="${GITHUB_REF/refs\/tags\//}"
echo "TAG is $TAG"
if ! [ -x "$(command -v poetry)" ]; then
    echo 'Poetry not found!' >&2
    exit 1
fi
VERSION="$(poetry version --no-ansi | cut -d' ' -f2)"
echo "VERSION is $VERSION"

if [[ "$GITHUB_REF" =~ refs\/tags\/.* && "$TAG" == "${VERSION}" ]]
then
    REV=""
    RELEASE="true"
else
    # PEP440 version scheme, different from semver 2.0
    REV=".dev${GITHUB_RUN_NUMBER:-0}+${GITHUB_SHA:0:8}"
    RELEASE="false"

    # Update version, so it will also show in the Gaphor application
    poetry version "${VERSION}${REV}"
fi

echo "version=${VERSION}${REV}" >> "$GITHUB_OUTPUT"
echo "release=${RELEASE}" >> "$GITHUB_OUTPUT"
