help:
clean:
	rm -rf dist target coverage \
	.coverage \
	src/kafka_emulator/__pycache__ \
	tests/__pycache__ \
	.pytest_cache  .tox
run-help:
	poetry run kafka-emulator -h
run-scenario:
	poetry run kafka-emulator -s testing/scenario.yaml
kafka-up:
	cd testing && docker compose up -d
kafka-down:
	cd testing && docker compose down
kafka-consume:
	docker exec kafka-test /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic test-topic --from-beginning --property print.key=true --property print.headers=true
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
one: clean set-version install flake8 build
	tox run -e py314
release:
	scripts/release.sh

tox-run:
	tox run
