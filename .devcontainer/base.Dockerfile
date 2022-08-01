# [Choice] Ubuntu version (use jammy or bionic on local arm64/Apple Silicon): jammy, focal, bionic
ARG VARIANT="jammy"
FROM buildpack-deps:${VARIANT}-curl

# Options for setup script
ARG INSTALL_ZSH="true"
ARG UPGRADE_PACKAGES="true"
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID
ARG PYTHON_VERSION="3.10.5"

COPY .devcontainer/library-scripts/*.sh .devcontainer/library-scripts/*.env /tmp/library-scripts/

RUN yes | unminimize 2>&1 \ 
    && bash /tmp/library-scripts/common-debian.sh "${INSTALL_ZSH}" "${USERNAME}" "${USER_UID}" "${USER_GID}" "${UPGRADE_PACKAGES}" "true" "true" \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*

ENV PIPX_HOME=/usr/local/py-utils \
    PIPX_BIN_DIR=/usr/local/py-utils/bin
ENV PATH=${PATH}:${PIPX_BIN_DIR}
COPY .devcontainer/library-scripts/*.sh .devcontainer/library-scripts/*.env /tmp/library-scripts/
RUN bash /tmp/library-scripts/python-debian.sh "${PYTHON_VERSION}" "/usr/local/python" "${PIPX_HOME}" "${USERNAME}" \ 
    && apt-get clean -y && rm -rf /var/lib/apt/lists/* /tmp/library-scripts

# Install additional OS packages.
RUN apt-get update -qq && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install -qq --no-install-recommends libcairo2-dev \
    pkg-config python3-dev gir1.2-gtk-4.0 libgirepository1.0-dev \
    libgtksourceview-5-dev libadwaita-1-dev \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# Config poetry
RUN poetry config virtualenvs.in-project true
