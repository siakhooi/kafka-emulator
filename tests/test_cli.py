import datetime
import sys
import uuid

from kafka_emulator.cli import render_template, run
from kafka_emulator.template_helpers import get_template_helpers

import pytest


@pytest.mark.parametrize("option_help", ["-h", "--help"])
@pytest.mark.skipif(
    sys.version_info < (3, 13),
    reason="Help output format differs in Python < 3.13",
)
def test_run_help(monkeypatch, capsys, option_help):
    monkeypatch.setenv("COLUMNS", "80")
    monkeypatch.setattr(
        "sys.argv",
        ["kafka-emulator", option_help],
    )

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        run()
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    with open("tests/expected-output/cli-help.txt", "r") as f:
        expected_output = f.read()

    captured = capsys.readouterr()
    assert captured.out == expected_output


@pytest.mark.parametrize("option_help", ["-h", "--help"])
@pytest.mark.skipif(
    sys.version_info >= (3, 13),
    reason="Help output format differs in Python >= 3.13",
)
def test_run_help312(monkeypatch, capsys, option_help):
    monkeypatch.setenv("COLUMNS", "80")
    monkeypatch.setattr(
        "sys.argv",
        ["kafka-emulator", option_help],
    )

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        run()
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    with open("tests/expected-output/cli-help312.txt", "r") as f:
        expected_output = f.read()

    captured = capsys.readouterr()
    assert captured.out == expected_output


@pytest.mark.parametrize("option_version", ["-v", "--version"])
def test_run_show_version(monkeypatch, capsys, option_version):
    monkeypatch.setattr(
        "sys.argv",
        ["kafka-emulator", option_version],
    )

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        run()
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 0

    with open("tests/expected-output/cli-version.txt", "r") as f:
        expected_output = f.read()

    captured = capsys.readouterr()
    assert captured.out == expected_output


@pytest.mark.parametrize("options", [["-p"], ["-p", "-j"]])
def test_run_wrong_options(monkeypatch, capsys, options):
    monkeypatch.setattr(
        "sys.argv",
        ["kafka-emulator"] + options,
    )

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        run()
    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 2

    captured = capsys.readouterr()
    assert "usage: kafka-emulator [-h] [-v] [-s SCENARIO]" in captured.err
    assert "kafka-emulator: error: unrecognized arguments:" in captured.err


def test_render_template_helpers_uuid_and_now():
    rendered_uuid = render_template("{{ uuid() }}", {})
    assert isinstance(rendered_uuid, str)
    assert rendered_uuid
    assert len(rendered_uuid) >= 32

    uuid_obj = uuid.UUID(rendered_uuid)
    assert str(uuid_obj) == rendered_uuid

    rendered_now = render_template("{{ now() }}", {})
    assert isinstance(rendered_now, str)
    datetime.datetime.fromisoformat(rendered_now)


def test_template_helpers_are_exposed_via_map():
    helpers = get_template_helpers()
    assert "uuid" in helpers
    assert callable(helpers["uuid"])
    assert "now" in helpers
    assert callable(helpers["now"])
