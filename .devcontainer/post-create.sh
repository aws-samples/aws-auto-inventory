#!/usr/bin/env bash

set -eu pipefail

export DEBIAN_FRONTEND=noninteractive

sudo apt-get update
sudo apt-get -y install --no-install-recommends \
	bash-completion \
    make

make pre-commit/install

pip3 install --user -r requirements.txt

clear
devcontainer-info
