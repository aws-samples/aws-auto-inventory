export WORKSPACE=$(shell pwd)
export HABITS = $(WORKSPACE)/habits

#include $(WORKSPACE)/tools.env # pin the version of your tools
#include $(WORKSPACE)/dev.env # don't store secrets in git
#include $(WORKSPACE)/dev.secrets.env # remember to add *.secrets.env to .gitignore

include $(HABITS)/lib/make/Makefile
include $(HABITS)/lib/make/*/Makefile

# You can change this tag to suit your needs
TAG=$(shell date +%Y%m%d)
OS=$(shell uname -s | tr A-Z a-z)
ARCH=$(shell uname -m | tr A-Z a-z)

.PHONY: clean
clean:
	@rm -rf build/ dist/ *.spec log/ output/ build.txt __pycache__/ aai/__pycache__/ output/

.PHONY: build
build: clean
	@( \
       . $(WORKSPACE)/.venv/bin/activate; \
	   pyinstaller --name aws-auto-inventory-$(OS)-$(ARCH) --clean --onefile --hidden-import cmath --log-level=DEBUG cli.py 2> build.txt; \
    )

.PHONY: run
run:
	@( \
       . $(WORKSPACE)/.venv/bin/activate; \
		python app/cli.py --name=learning; \
	)
