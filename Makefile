.PHONY: format lint typecheck check

format:
	black .
	isort .

lint:
	flake8 src

typecheck:
	mypy src

test:
	python -m pytest .

check: format lint typecheck test
