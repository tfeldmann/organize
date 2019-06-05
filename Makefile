.PHONY: upload upload_prod clean docs

dist:
	poetry build

upload: dist
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*
	@echo Success.
	@echo
	@echo "Test install with:"
	@echo "    pip3 install --index-url https://test.pypi.org/simple/ organize-tool"
	@echo "Upload to production:"
	@echo "    make upload_prod"

upload_prod: dist
	twine upload dist/*
	@echo Success.

clean:
	rm -fr build dist .egg organize_tool.egg-info

docs:
	cd docs && make html
	@echo Build successful! View the docs at docs/_build/html/index.html
