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
	find src/${PROJECT}/ tests/ -name __pycache__ | xargs rm -rf
	find src/${PROJECT}/ tests/ -name '*.pyc' | xargs rm -rf

.PHONY: format
format:  ## Format files
	tox exec -e py39-lint -- ruff format

.PHONY: lint
lint:  ## Lint files
	tox -e py39-lint

.PHONY: test
test:  ## Run tox to test across supported Python versions
	tox

.PHONY: docs
docs:  ## Build docs
	make -C docs/ clean
	make -C docs/ doctest
	make -C docs/ html
