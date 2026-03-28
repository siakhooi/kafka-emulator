help:
clean:
	rm -rf dist target coverage \
	.coverage \
	src/kafka_mocker/__pycache__ \
	tests/__pycache__ \
	.pytest_cache
run:
	poetry run kafka-mocker
set-version:
	scripts/set-version.sh
build:
	poetry build
install:
	poetry install
flake8:
	poetry run flake8
update:
	poetry update
test:
	 poetry run pytest --capture=sys \
	 --junit-xml=coverage/test-results.xml \
	 --cov=kafka_mocker \
	 --cov-report term-missing  \
	 --cov-report xml:coverage/coverage.xml \
	 --cov-report html:coverage/coverage.html \
	 --cov-report lcov:coverage/coverage.info

all: clean set-version install flake8 build test

release:
	scripts/release.sh

commit:
	scripts/git-commit.sh
	git push

fix-cert:
	pip install pip-system-certs --trusted-host pypi.org --trusted-host files.pythonhosted.org
