.PHONY: help setup test publish flask_saml.zip clean pipelines_requirements docs

help:
	@echo "Available commands:"
	@echo "  setup:    Build for development"
	@echo "  test:     Test module"
	@echo "  publish:  Publish to PyPI"
	@echo "  clean:    Clean up temporary files"
	@echo "  docs:     Build HTML docs using docs/Makefile"

~/.pypirc:
	cp .pipelines-pypirc ~/.pypirc
	sed -i "s/username:/username: ${PYPI_USER}/g" ~/.pypirc
	sed -i "s/password:/password: ${PYPI_PASS}/g" ~/.pypirc

setup:
	python setup.py develop

test:
	python setup.py test

publish: ~/.pypirc
	python setup.py sdist
	twine upload -r pypi dist/*

clean:
	rm -rf .eggs .cache .coverage htmlcov dist Flask_SAML.egg-info
	find . -type d -name '__pycache__' -exec rm -rf '{}' \; || exit 0
	find . -name '*.pyc' -exec rm -rf '{}' \;
	make -C docs/ clean

pipelines_requirements: ~/.pypirc
	pip -q install sphinx twine
	pip -q install -r docs/requirements.txt

docs: setup
	make -C docs/ html
