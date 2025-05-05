.PHONY: format lint typecheck check

format:
	black .
	isort .

lint:
	flake8 src

typecheck:
	mypy src

check: format lint typecheck
