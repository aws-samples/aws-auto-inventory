.PHONY: init
init:
	python3 -m venv .venv
	@( \
       source .venv/bin/activate; \
	   pip install --upgrade pip ; \
	   pip install --upgrade pyinstaller ; \
       pip install -r requirements.txt; \
    )

.PHONY: clean
clean:
	@rm -rf build/ dist/ *.spec log/ output/ build.txt __pycache__/ aai/__pycache__/ 

.PHONY: dist
dist: clean
	@( \
       source .venv/bin/activate; \
	   pyinstaller --name aws-auto-inventory --clean --onefile --hidden-import cmath --log-level=DEBUG cli.py 2> build.txt; \
    )
	
