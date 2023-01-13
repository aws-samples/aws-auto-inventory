ARG VARIANT="jammy"
FROM mcr.microsoft.com/vscode/devcontainers/base:0-${VARIANT}

# Install OS packages
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    make

USER vscode

RUN cd /tmp/ \
    && git clone https://github.com/awslabs/aws-code-habits.git \
    && cd aws-code-habits \
    && make devcontainer/init aws/cli/install/v2 aws/cli/autocomplete \
    && rm -rf /tmp/aws-code-habits

# Add pip requirements
COPY requirements.txt /tmp/
RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/requirements.txt \
   && rm -rf /tmp/pip-tmp

USER root
