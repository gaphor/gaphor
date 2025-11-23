FROM mcr.microsoft.com/vscode/devcontainers/base:debian

# Install additional OS packages.
RUN apt-get update -qq && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install -qq --no-install-recommends libcairo2-dev \
    pkg-config python3-dev gir1.2-gtk-4.0 libgirepository-2.0-dev \
    libgtksourceview-5-dev libadwaita-1-dev graphviz \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*
