.PHONY: init
init:
	python3 -m venv .venv
	( \
       source .venv/bin/activate; \
	   pip install --upgrade pip ; \
       pip install -r requirements.txt; \
    )

.PHONY: clean
clean:
	rm -rf build dist *.spec

.PHONY: dist
dist: clean
	pyinstaller --name aws-auto-inventory main.py
