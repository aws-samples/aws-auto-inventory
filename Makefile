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
	rm -rf build/ dist/ *.spec log/ output/ build.txt

.PHONY: dist
dist: clean
	pyinstaller --name aws-auto-inventory --clean --onefile --log-level=DEBUG cli.py 2> build.txt
