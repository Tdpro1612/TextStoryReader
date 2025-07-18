.PHONY: format clean help
.PHONY: lint
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
	poetry run ruff format . # Code Formatter pep8, Sorts imports library, pylint logic
	@echo "Python code formatted successfully."

fix:
	@echo "fix some python code...."
	poetry run ruff check . --fix
	@echo "fix done with ruff"
# If you prefer to use lint :
lint:
	@echo "Scoring Python code using pylint..."
    # Sử dụng poetry run để đảm bảo pylint được chạy từ môi trường ảo của dự án
    # Chỉ định rõ pyproject.toml làm file cấu hình
    # Chỉ định thư mục mã nguồn chính của bạn (textstoryreader/) để pylint chỉ kiểm tra code của bạn
	poetry run pylint --rcfile=pyproject.toml textstoryreader/
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