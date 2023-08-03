export WORKSPACE=$(shell pwd)
export HABITS = $(WORKSPACE)/habits

include $(HABITS)/lib/make/Makefile
include $(HABITS)/lib/make/*/Makefile

.PHONY: clean
## Clean project
clean:
	@rm -rf output/

.PHONY: hygiene
hygiene: doc/build pre-commit/run
