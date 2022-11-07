DEFAULT_GOAL := help
PROJECT=markus

.PHONY: help
help:
	@echo "Available rules:\n"
	@fgrep -h "##" Makefile | fgrep -v fgrep | sed 's/\(.*\):.*##/\1:/'

.PHONY: clean
clean:  ## Clean build artifacts
	rm -rf build dist src/${PROJECT}.egg-info .tox
	rm -rf docs/_build/*
	find ${PROJECT}/ tests/ -name __pycache__ | xargs rm -rf
	find ${PROJECT}/ tests/ -name '*.pyc' | xargs rm -rf

.PHONY: lint
lint:  ## Lint and black reformat files
	black --target-version=py37 --line-length=88 src setup.py tests
	tox -e py37-flake8

.PHONY: test
test:  ## Run tox to test across supported Python versions
	tox

.PHONY: checkrot
checkrot:  ## Check package rot for dev dependencies
	python -m venv ./tmpvenv/
	./tmpvenv/bin/pip install -U pip
	./tmpvenv/bin/pip install -r requirements-dev.txt
	./tmpvenv/bin/pip list -o
	rm -rf ./tmpvenv/

.PHONY: docs
docs:  ## Build docs
	make -C docs/ clean
	make -C docs/ doctest
	make -C docs/ html
