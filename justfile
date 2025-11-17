# Justfile for pretalx development tasks
# See https://github.com/casey/just for installation and documentation

# list available commands
default:
	@{{ just_executable() }} --list

# install all dependencies (dev, devdocs, postgres, redis)
install:
	uv sync --all-extras

# run the development server
run:
	cd src && uv run python manage.py runserver

# run the development server with automatic JS rebuilding
devserver:
	cd src && uv run python manage.py devserver

# run Django management commands
manage *args:
	cd src && uv run python manage.py {{ args }}

# apply database migrations
migrate:
	cd src && uv run python manage.py migrate

# collect static files
collectstatic:
	cd src && uv run python manage.py collectstatic --noinput

# create initial admin user, organiser and team
init:
	cd src && uv run python manage.py init

# create a test event with submissions and speakers
create-test-event stage="schedule":
	cd src && uv run python manage.py create_test_event --stage {{ stage }}

# run all code quality checks
check: black-check isort-check flake8 djhtml-check

# format code with black (check only)
black-check *args=".":
	uv run black --check {{ args }}

# format code with black
black *args=".":
	uv run black {{ args }}

# check import sorting with isort (check only)
isort-check *args=".":
	uv run isort --check {{ args }}

# sort imports with isort
isort *args=".":
	uv run isort {{ args }}

# run flake8 linter
flake8 *args=".":
	uv run flake8 {{ args }}

# format Django templates with djhtml (check only)
djhtml-check:
	#!/usr/bin/env bash
	set -euo pipefail
	# djhtml doesn't have a check mode, so we check if files would change
	files=$(find src -name "*.html" -type f)
	if [ -n "$files" ]; then
		for file in $files; do
			if ! diff -q "$file" <(uv run djhtml -t 2 "$file" | cat) >/dev/null; then
				echo "Would reformat: $file"
				exit 1
			fi
		done
	fi

# format Django templates with djhtml
djhtml:
	find src -name "*.html" -type f | xargs uv run djhtml -i -t 2

# fix all code formatting and style issues
fix: black isort djhtml

# run the test suite
test *args="":
	cd src && uv run pytest {{ args }}

# run tests with coverage report
test-coverage *args="":
	cd src && uv run pytest --cov=pretalx --cov-report=html --cov-report=term {{ args }}

# compile translation files
compilemessages:
	cd src && uv run python manage.py compilemessages

# update translation files (requires npm dependencies for schedule-editor)
makemessages:
	#!/usr/bin/env bash
	set -euo pipefail
	cd src/pretalx/frontend/schedule-editor
	npm ci
	cd ../../../
	uv run python manage.py makemessages --keep-pot --all

# rebuild static assets (JS, CSS) - installs npm dependencies
rebuild:
	cd src && uv run python manage.py rebuild --npm-install

# rebuild static assets without installing npm dependencies
rebuild-quick:
	cd src && uv run python manage.py rebuild

# open Django shell
shell:
	cd src && uv run python manage.py shell --unsafe-disable-scopes

# run type checks (if mypy is configured in the future)
# type-check:
# 	uv run mypy src/pretalx

# clean up generated files
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache
	rm -rf .coverage htmlcov
	rm -rf dist build

# run a specific test file or test case
test-file file *args="":
	cd src && uv run pytest {{ file }} {{ args }}

# run tests matching a keyword expression
test-k keyword *args="":
	cd src && uv run pytest -k {{ keyword }} {{ args }}

# run tests in parallel (requires pytest-xdist)
test-parallel n="auto" *args="":
	cd src && uv run pytest -n {{ n }} {{ args }}

# CI: run all checks and tests (what CI should run)
ci: check test

# show test coverage report in browser
coverage-report:
	{{ just_executable() }} test-coverage
	open htmlcov/index.html || xdg-open htmlcov/index.html || echo "Coverage report generated in htmlcov/index.html"
