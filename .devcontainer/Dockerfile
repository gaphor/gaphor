# [Choice] Ubuntu version (use ubuntu-22.04 or ubuntu-18.04 on local arm64/Apple Silicon): ubuntu-22.04, ubuntu-20.04, ubuntu-18.04
ARG VARIANT=ubuntu-22.04
FROM mcr.microsoft.com/vscode/devcontainers/base:0-${VARIANT}

# Install additional OS packages.
RUN apt-get update -qq && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install -qq --no-install-recommends libcairo2-dev \
    pkg-config python3-dev gir1.2-gtk-4.0 libgirepository1.0-dev \
    libgtksourceview-5-dev libadwaita-1-dev \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*
