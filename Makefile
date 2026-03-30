help:
clean:
	rm -rf dist target coverage \
	.coverage \
	src/kafka_emulator/__pycache__ \
	tests/__pycache__ \
	.pytest_cache  .tox
run:
	poetry run kafka-emulator
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
	 --cov=kafka_emulator \
	 --cov-report term-missing  \
	 --cov-report xml:coverage/coverage.xml \
	 --cov-report html:coverage/coverage.html \
	 --cov-report lcov:coverage/coverage.info

all: clean set-version install flake8 build tox-run

release:
	scripts/release.sh

tox-run:
	tox run
