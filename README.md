# kafka-emulator

`kafka-emulator` is a command-line tool for sending messages to Kafka topics
using scenario files. Scenarios are defined in YAML and support Jinja2
templates for dynamic content generation.

## Documentation

- [User Guide](docs/user-guide.md) - Installation, Quick Start, Command Line Options
- [Scenario YAML Specification](docs/scenario-spec.md)

## Links

- https://pypi.org/project/kafka_emulator/
- https://github.com/siakhooi/kafka-emulator
- https://sonarcloud.io/project/overview?id=siakhooi_kafka-emulator
- https://qlty.sh/gh/siakhooi/projects/kafka-emulator

## Badges

![GitHub](https://img.shields.io/github/license/siakhooi/kafka-emulator?logo=github)
![GitHub last commit](https://img.shields.io/github/last-commit/siakhooi/kafka-emulator?logo=github)
![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/siakhooi/kafka-emulator?logo=github)
![GitHub issues](https://img.shields.io/github/issues/siakhooi/kafka-emulator?logo=github)
![GitHub closed issues](https://img.shields.io/github/issues-closed/siakhooi/kafka-emulator?logo=github)
![GitHub pull requests](https://img.shields.io/github/issues-pr-raw/siakhooi/kafka-emulator?logo=github)
![GitHub closed pull requests](https://img.shields.io/github/issues-pr-closed-raw/siakhooi/kafka-emulator?logo=github)
![GitHub top language](https://img.shields.io/github/languages/top/siakhooi/kafka-emulator?logo=github)
![GitHub language count](https://img.shields.io/github/languages/count/siakhooi/kafka-emulator?logo=github)
![Lines of code](https://img.shields.io/tokei/lines/github/siakhooi/kafka-emulator?logo=github)
![GitHub repo size](https://img.shields.io/github/repo-size/siakhooi/kafka-emulator?logo=github)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/siakhooi/kafka-emulator?logo=github)

![Workflow](https://img.shields.io/badge/Workflow-github-purple)
![workflow](https://github.com/siakhooi/kafka-emulator/actions/workflows/build.yaml/badge.svg)
![workflow](https://github.com/siakhooi/kafka-emulator/actions/workflows/workflow-deployments.yml/badge.svg)

![Release](https://img.shields.io/badge/Release-github-purple)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/siakhooi/kafka-emulator?label=GPR%20release&logo=github)
![GitHub all releases](https://img.shields.io/github/downloads/siakhooi/kafka-emulator/total?color=33cb56&logo=github)
![GitHub Release Date](https://img.shields.io/github/release-date/siakhooi/kafka-emulator?logo=github)

![Quality-Qlty](https://img.shields.io/badge/Quality-Qlty-purple)
[![Maintainability](https://qlty.sh/gh/siakhooi/projects/kafka-emulator/maintainability.svg)](https://qlty.sh/gh/siakhooi/projects/kafka-emulator)
[![Code Coverage](https://qlty.sh/gh/siakhooi/projects/kafka-emulator/coverage.svg)](https://qlty.sh/gh/siakhooi/projects/kafka-emulator)

![Quality-Sonar](https://img.shields.io/badge/Quality-SonarCloud-purple)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=siakhooi_kafka-emulator&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=siakhooi_kafka-emulator)
[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=siakhooi_kafka-emulator&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=siakhooi_kafka-emulator)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=siakhooi_kafka-emulator&metric=bugs)](https://sonarcloud.io/summary/new_code?id=siakhooi_kafka-emulator)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=siakhooi_kafka-emulator&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=siakhooi_kafka-emulator)
[![Technical Debt](https://sonarcloud.io/api/project_badges/measure?project=siakhooi_kafka-emulator&metric=sqale_index)](https://sonarcloud.io/summary/new_code?id=siakhooi_kafka-emulator)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=siakhooi_kafka-emulator&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=siakhooi_kafka-emulator)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=siakhooi_kafka-emulator&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=siakhooi_kafka-emulator)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=siakhooi_kafka-emulator&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=siakhooi_kafka-emulator)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=siakhooi_kafka-emulator&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=siakhooi_kafka-emulator)
[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=siakhooi_kafka-emulator&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=siakhooi_kafka-emulator)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=siakhooi_kafka-emulator&metric=coverage)](https://sonarcloud.io/summary/new_code?id=siakhooi_kafka-emulator)
![Sonar Violations (short format)](https://img.shields.io/sonar/violations/siakhooi_kafka-emulator?server=https%3A%2F%2Fsonarcloud.io)
![Sonar Violations (short format)](https://img.shields.io/sonar/blocker_violations/siakhooi_kafka-emulator?server=https%3A%2F%2Fsonarcloud.io)
![Sonar Violations (short format)](https://img.shields.io/sonar/critical_violations/siakhooi_kafka-emulator?server=https%3A%2F%2Fsonarcloud.io)
![Sonar Violations (short format)](https://img.shields.io/sonar/major_violations/siakhooi_kafka-emulator?server=https%3A%2F%2Fsonarcloud.io)
![Sonar Violations (short format)](https://img.shields.io/sonar/minor_violations/siakhooi_kafka-emulator?server=https%3A%2F%2Fsonarcloud.io)
![Sonar Violations (short format)](https://img.shields.io/sonar/info_violations/siakhooi_kafka-emulator?server=https%3A%2F%2Fsonarcloud.io)
![Sonar Violations (long format)](https://img.shields.io/sonar/violations/siakhooi_kafka-emulator?format=long&server=http%3A%2F%2Fsonarcloud.io)

[![Wise](https://img.shields.io/badge/Funding-Wise-33cb56.svg?logo=wise)](https://wise.com/pay/me/siakn3)
![visitors](https://hit-tztugwlsja-uc.a.run.app/?outputtype=badge&counter=ghmd-kafka-emulator)
