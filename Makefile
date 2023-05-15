SRC_DIRS := $(shell find . -maxdepth 1 -type d -not -name '.*')

lint:
	flake8 $(SRC_DIRS)
	isort --check-only --diff $(SRC_DIRS)
	black --check $(SRC_DIRS)
	mypy --ignore-missing-imports $(SRC_DIRS)

format:
	isort $(SRC_DIRS)
	black $(SRC_DIRS)

mypy:
	mypy --ignore-missing-imports $(SRC_DIRS)
