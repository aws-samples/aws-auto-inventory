export WORKSPACE=$(shell pwd)
export HABITS = $(WORKSPACE)/habits

include $(HABITS)/lib/make/Makefile
include $(HABITS)/lib/make/*/Makefile

# You can change this tag to suit your needs
TAG?=$(shell date +%Y%m%d)
OS?=$(shell uname -s | tr A-Z a-z)
ARCH?=$(shell uname -m | tr A-Z a-z)

.PHONY: app/clean
##
app/clean:
	@rm -rf build/ dist/ *.spec log/ output/ build.txt __pycache__/ aai/__pycache__/ output/

.PHONY: app/build
app/build: app/clean
	@pyinstaller --name aws-auto-inventory-$(OS)-$(ARCH) --clean --onefile --hidden-import cmath --log-level=DEBUG app/cli.py 2> build.log

.PHONY: app/run
app/run:
	@python3 app/cli.py --name=learning

.PHONY: app/run/build
app/run/build:
	@dist/aws-auto-inventory-$(OS)-$(ARCH) --name=learning
