export WORKSPACE=$(shell pwd)
export HABITS = $(WORKSPACE)/habits

include $(HABITS)/lib/make/Makefile
include $(HABITS)/lib/make/*/Makefile

.PHONY: app/clean
## Clean project
app/clean:
	@rm -rf output/

.PHONY: hygiene
hygiene: doc/build pre-commit/run
