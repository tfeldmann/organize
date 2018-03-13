.PHONY: docs
init:
	pip install pipenv --upgrade
	pipenv install --dev --skip-lock

test:
	pipenv run py.test tests

publish:
	python setup.py sdist upload -r pypi

docs:
	cd docs && make html
	@echo "\033[95m\n\nBuild successful! View the docs homepage at docs/_build/html/index.html.\n\033[0m"
