PYTHON=python3
VENV=venv
PIP=$(VENV)/bin/pip
PY=$(VENV)/bin/python

.PHONY: install test run run-server run-client server client clean freeze

install:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	if [ -f requirements.txt ]; then $(PIP) install -r requirements.txt; fi

test:
	$(PY) -m unittest discover -s tests -v

run:
	$(PY) main.py cliente

run-server:
	$(PY) main.py servidor

run-client:
	$(PY) main.py cliente

server:
	$(PY) main.py servidor

client:
	$(PY) main.py cliente

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

freeze:
	$(PIP) freeze > requirements.txt