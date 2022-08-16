# [Choice] Python version (use -bullseye variants on local arm64/Apple Silicon): 3, 3.10, 3.9, 3.8, 3.7, 3.6, 3-bullseye, 3.10-bullseye, 3.9-bullseye, 3.8-bullseye, 3.7-bullseye, 3.6-bullseye, 3-buster, 3.10-buster, 3.9-buster, 3.8-buster, 3.7-buster, 3.6-buster
ARG VARIANT=3-bullseye
FROM mcr.microsoft.com/vscode/devcontainers/python:${VARIANT}

# [Choice] Node.js version: none, lts/*, 16, 14, 12, 10
ARG NODE_VERSION="none"
RUN if [ "${NODE_VERSION}" != "none" ]; then su vscode -c "umask 0002 && . /usr/local/share/nvm/nvm.sh && nvm install ${NODE_VERSION} 2>&1"; fi

# Add pip requirements
COPY requirements.txt /tmp/pip-tmp/
RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \
   && rm -rf /tmp/pip-tmp

# Install additional OS packages.
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends bash-completion figlet

# [Optional] Uncomment this line to install global node packages.
# RUN su vscode -c "source /usr/local/share/nvm/nvm.sh && npm install -g <your-package-here>" 2>&1

# Get the lastest version of pip
RUN /usr/local/bin/python -m pip install --upgrade pip

# Install pre-commit
RUN /usr/local/bin/python -m pip install pre-commit

# Install pyinstaller
RUN /usr/local/bin/python -m pip install pyinstaller

# Gitignore CLI
ARG REMOTE_USER=vscode
RUN echo "function gi() { curl -sL https://www.toptal.com/developers/gitignore/api/\$@ ;}" >> /home/${REMOTE_USER}/.bashrc
RUN echo "function gi() { curl -sLw "\n" https://www.toptal.com/developers/gitignore/api/\$@ ;}" >> /home/${REMOTE_USER}/.zshrc

RUN mkdir -p /home/${REMOTE_USER}/.config/aws-auto-inventory
COPY .devcontainer/config.yaml /home/${REMOTE_USER}/.config/aws-auto-inventory/
RUN chown -R ${REMOTE_USER}:${REMOTE_USER} /home/${REMOTE_USER}

RUN wget --quiet https://github.com/awslabs/clencli/releases/download/0.3.6/clencli-linux-amd64 \
    && mv clencli-linux-amd64 /usr/local/bin/clencli \
    && chmod +x /usr/local/bin/clencli
