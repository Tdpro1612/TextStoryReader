.PHONY: format clean help

# Default target
all: help

# Help message
help:
	@echo "Available commands:"
	@echo "  make format       - Format Python code using black and isort/ruff"
	@echo "  make clean        - Clean build artifacts (e.g., buildozer temporary files)"
	@echo "  make build        - Run buildozer to build the Android app"

# Target to format Python code
# Using black for formatting and isort for sorting imports
# You can choose either black+isort OR ruff format
format:
	@echo "Formatting Python code..."
	ruff format . # Code Formatter pep8, Sorts imports library, pylint logic
	@echo "Python code formatted successfully."

fix:
	@echo "fix some python code...."
	ruff check . --fix
	@echo "fix done with ruff"
# If you prefer to use lint :
lint:
	@echo "Scoring Python code using pylint..."
	pylint $(shell find . -name "*.py" -print) --ignore=__init__.py
	@echo "Python code score with pylint."


# Target to clean buildozer temporary files
clean:
	@echo "Cleaning buildozer temporary files..."
	buildozer android clean
	rm -rf .buildozer/
	@echo "Clean complete."

# Target to run buildozer build
build: clean
	@echo "Starting Android app build..."
	buildozer android debug
	@echo "Build process initiated."