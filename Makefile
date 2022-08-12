# You can change this tag to suit your needs
TAG=$(shell date +%Y%m%d)
OS=$(shell uname -s | tr A-Z a-z)
ARCH=$(shell uname -m | tr A-Z a-z)

.PHONY: init
init:
	python3 -m venv .venv
	@( \
       . .venv/bin/activate; \
	   pip install --upgrade pip ; \
	   pip install --upgrade pyinstaller ; \
       pip install -r requirements.txt; \
    )

.PHONY: clean
clean:
	@rm -rf build/ dist/ *.spec log/ output/ build.txt __pycache__/ aai/__pycache__/

.PHONY: build
build: clean
	@( \
       . .venv/bin/activate; \
	   pyinstaller --name aws-auto-inventory-$(OS)-$(ARCH) --clean --onefile --hidden-import cmath --log-level=DEBUG cli.py 2> build.txt; \
    )

.PHONY: pre-commit/install-hooks
## Install pre-commit hooks
pre-commit/install-hooks:
	pre-commit install

.PHONY: pre-commit/update
##  Update pre-commit-config.yml with the latest version
pre-commit/update:
	pre-commit autoupdate

.PHONY: pre-commit/run
## Execute pre-commit hooks on all files
pre-commit/run:
	pre-commit run --all-files

.PHONY: pre-commit/version
## Display pre-commit version
pre-commit/version:
	@echo "--- PRE-COMMIT ---"
	@pre-commit --version

.PHONY: python/version
## Display Python & Pip version
python/version:
	@echo "--- PYTHON 3 ---"
	@python3 --version
	@echo "--- PIP ---"
	@pip3 --version

aws-auto-inventory/run:
	@python cli.py
