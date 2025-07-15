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

# If you prefer to use Ruff (which can do both formatting and import sorting):
# format_ruff:
# 	@echo "Formatting Python code using Ruff..."
# 	ruff format .
# 	@echo "Python code formatted successfully with Ruff."


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