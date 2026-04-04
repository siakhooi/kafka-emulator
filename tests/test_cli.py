import datetime
import json
import signal
import sys
import uuid
from unittest.mock import MagicMock

import yaml

from kafka_emulator.cli import (
    _build_run_context,
    _handle_pause,
    _handle_send,
    _handle_set,
    _handle_sleep,
    _print_step,
    print_to_stderr_and_exit,
    render_template,
    run,
    run_scenario,
    wait_for_keypress,
)
from kafka_emulator.models import Step
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


class TestPrintStep:
    def test_prints_tagged_message(self, capsys):
        _print_step("TEST", "\033[32m", "hello")
        captured = capsys.readouterr()
        assert "[TEST]" in captured.out
        assert "hello" in captured.out


class TestPrintToStderrAndExit:
    def test_prints_error_and_exits(self, capsys):
        with pytest.raises(SystemExit) as exc:
            print_to_stderr_and_exit(ValueError("boom"), 42)
        assert exc.value.code == 42
        captured = capsys.readouterr()
        assert "Error: boom" in captured.err


class TestWaitForKeypress:
    def test_non_tty_with_timeout(self, monkeypatch):
        monkeypatch.setattr("sys.stdin.isatty", lambda: False)
        start = datetime.datetime.now()
        wait_for_keypress(0.05)
        elapsed = (datetime.datetime.now() - start).total_seconds()
        assert elapsed >= 0.04

    def test_non_tty_without_timeout(self, monkeypatch):
        monkeypatch.setattr("sys.stdin.isatty", lambda: False)
        wait_for_keypress(None)


class TestRenderTemplate:
    def test_returns_none_for_none(self):
        assert render_template(None, {}) is None

    def test_renders_plain_string(self):
        assert render_template("hello", {}) == "hello"

    def test_renders_context_variable(self):
        assert render_template("{{ x }}", {"x": "val"}) == "val"

    def test_renders_helper(self):
        result = render_template("{{ epoch() }}", {})
        assert int(result) > 0

    def test_helpers_override_context(self):
        result = render_template(
            "{{ now }}",
            {"now": "custom"},
        )
        # helpers override context keys with same name
        assert result != "custom"


class TestBuildRunContext:
    def test_returns_required_keys(self):
        ctx = _build_run_context("My Scenario")
        assert ctx["scenario_name"] == "My Scenario"
        assert "run_name" in ctx
        assert "run_datetime" in ctx
        assert "run_id" in ctx

    def test_run_name_normalized(self):
        ctx = _build_run_context("Hello World 123")
        assert ctx["run_name"].startswith("hello_world_123_")

    def test_run_id_is_uuid(self):
        ctx = _build_run_context("test")
        uuid.UUID(ctx["run_id"])

    def test_run_datetime_format(self):
        ctx = _build_run_context("test")
        datetime.datetime.strptime(ctx["run_datetime"], "%Y-%m-%dT%H:%M:%SZ")


class TestHandleSet:
    def test_sets_context_values(self, capsys):
        step = Step(set={"name": "alice", "age": "30"})
        context = {}
        _handle_set(step, context)
        assert context["name"] == "alice"
        assert context["age"] == "30"
        captured = capsys.readouterr()
        assert "[SET]" in captured.out
        assert "name = alice" in captured.out

    def test_renders_templates(self, capsys):
        step = Step(set={"greeting": "hello {{ name }}"})
        context = {"name": "bob"}
        _handle_set(step, context)
        assert context["greeting"] == "hello bob"


class TestHandleSend:
    def test_sends_message(self, tmp_path, capsys):
        body_file = tmp_path / "msg.json"
        body_file.write_text('{"key": "value"}')

        step = Step(
            send={
                "topic": "test-topic",
                "body": "msg.json",
                "key": "k1",
            }
        )
        producer = MagicMock()
        _handle_send(step, {}, {}, tmp_path, producer)

        producer.send.assert_called_once()
        call_kwargs = producer.send.call_args
        assert call_kwargs.kwargs["topic"] == "test-topic"
        assert call_kwargs.kwargs["key"] == "k1"
        producer.flush.assert_called_once()

        captured = capsys.readouterr()
        assert "[SEND]" in captured.out
        assert "test-topic" in captured.out

    def test_minifies_json_body(self, tmp_path, capsys):
        body_file = tmp_path / "msg.json"
        body_file.write_text('{ "a" :  1 ,  "b" : 2 }')

        step = Step(
            send={
                "topic": "t",
                "body": "msg.json",
            }
        )
        producer = MagicMock()
        _handle_send(step, {}, {}, tmp_path, producer)

        sent_body = producer.send.call_args.kwargs["value"]
        assert sent_body == '{"a":1,"b":2}'

    def test_non_json_body_unchanged(self, tmp_path, capsys):
        body_file = tmp_path / "msg.txt"
        body_file.write_text("plain text")

        step = Step(
            send={
                "topic": "t",
                "body": "msg.txt",
            }
        )
        producer = MagicMock()
        _handle_send(step, {}, {}, tmp_path, producer)

        sent_body = producer.send.call_args.kwargs["value"]
        assert sent_body == "plain text"

    def test_merges_default_and_step_headers(
        self,
        tmp_path,
        capsys,
    ):
        body_file = tmp_path / "msg.txt"
        body_file.write_text("body")

        step = Step(
            send={
                "topic": "t",
                "body": "msg.txt",
                "headers": {"x-step": "s1"},
            }
        )
        producer = MagicMock()
        default_headers = {"x-default": "d1"}
        _handle_send(
            step,
            {},
            default_headers,
            tmp_path,
            producer,
        )

        sent_headers = producer.send.call_args.kwargs["headers"]
        header_keys = [h[0] for h in sent_headers]
        assert "x-default" in header_keys
        assert "x-step" in header_keys

    def test_step_headers_override_defaults(
        self,
        tmp_path,
        capsys,
    ):
        body_file = tmp_path / "msg.txt"
        body_file.write_text("body")

        step = Step(
            send={
                "topic": "t",
                "body": "msg.txt",
                "headers": {"ct": "xml"},
            }
        )
        producer = MagicMock()
        default_headers = {"ct": "json"}
        _handle_send(
            step,
            {},
            default_headers,
            tmp_path,
            producer,
        )

        sent_headers = producer.send.call_args.kwargs["headers"]
        header_dict = {h[0]: h[1] for h in sent_headers}
        assert header_dict["ct"] == b"xml"

    def test_no_key(self, tmp_path, capsys):
        body_file = tmp_path / "msg.txt"
        body_file.write_text("body")

        step = Step(
            send={
                "topic": "t",
                "body": "msg.txt",
            }
        )
        producer = MagicMock()
        _handle_send(step, {}, {}, tmp_path, producer)

        assert producer.send.call_args.kwargs["key"] is None

    def test_renders_template_in_key(self, tmp_path, capsys):
        body_file = tmp_path / "msg.txt"
        body_file.write_text("body")

        step = Step(
            send={
                "topic": "t",
                "body": "msg.txt",
                "key": "{{ uid }}",
            }
        )
        producer = MagicMock()
        _handle_send(
            step,
            {"uid": "abc"},
            {},
            tmp_path,
            producer,
        )

        assert producer.send.call_args.kwargs["key"] == "abc"


class TestHandleSleep:
    def test_with_message(self, capsys, mocker):
        mocker.patch("kafka_emulator.cli.time.sleep")
        step = Step(sleep={"message": "waiting", "duration": "100ms"})
        _handle_sleep(step, {})
        captured = capsys.readouterr()
        assert "[SLEEP]" in captured.out
        assert "waiting" in captured.out

    def test_without_message(self, capsys, mocker):
        mocker.patch("kafka_emulator.cli.time.sleep")
        step = Step(sleep={"duration": "500ms"})
        _handle_sleep(step, {})
        captured = capsys.readouterr()
        assert "[SLEEP]" in captured.out
        assert "500ms" in captured.out

    def test_calls_sleep(self, mocker):
        mock_sleep = mocker.patch("kafka_emulator.cli.time.sleep")
        step = Step(sleep={"duration": "2s"})
        _handle_sleep(step, {})
        mock_sleep.assert_called_once_with(2.0)

    def test_renders_template_in_message(self, capsys, mocker):
        mocker.patch("kafka_emulator.cli.time.sleep")
        step = Step(sleep={"message": "hi {{ name }}"})
        _handle_sleep(step, {"name": "bob"})
        captured = capsys.readouterr()
        assert "hi bob" in captured.out


class TestHandlePause:
    def test_with_timeout(self, capsys, mocker):
        mocker.patch("kafka_emulator.cli.wait_for_keypress")
        step = Step(pause={"message": "wait", "timeout": "3s"})
        _handle_pause(step, {})
        captured = capsys.readouterr()
        assert "[PAUSE]" in captured.out
        assert "wait" in captured.out
        assert "timeout: 3s" in captured.out

    def test_without_timeout(self, capsys, mocker):
        mock_wait = mocker.patch(
            "kafka_emulator.cli.wait_for_keypress",
        )
        step = Step(pause={"message": "continue"})
        _handle_pause(step, {})
        captured = capsys.readouterr()
        assert "continue" in captured.out
        assert "Press any key to continue..." in captured.out
        mock_wait.assert_called_once_with(None)

    def test_no_message_with_timeout(self, capsys, mocker):
        mocker.patch("kafka_emulator.cli.wait_for_keypress")
        step = Step(pause={"timeout": "5s"})
        _handle_pause(step, {})
        captured = capsys.readouterr()
        assert "Press any key" in captured.out
        assert "timeout: 5s" in captured.out

    def test_no_message_no_timeout(self, capsys, mocker):
        mocker.patch("kafka_emulator.cli.wait_for_keypress")
        step = Step(pause={})
        _handle_pause(step, {})
        captured = capsys.readouterr()
        assert "Press any key to continue..." in captured.out

    def test_renders_template_in_message(self, capsys, mocker):
        mocker.patch("kafka_emulator.cli.wait_for_keypress")
        step = Step(pause={"message": "{{ x }}", "timeout": "1s"})
        _handle_pause(step, {"x": "done"})
        captured = capsys.readouterr()
        assert "done" in captured.out


class TestRunScenario:
    def test_runs_set_and_send(
        self,
        tmp_path,
        capsys,
        mocker,
    ):
        body_file = tmp_path / "msg.json"
        body_file.write_text('{"v": "{{ val }}"}')

        scenario = {
            "name": "test",
            "kafka": {
                "default": {
                    "bootstrap_servers": "localhost:9092",
                },
            },
            "steps": [
                {"set": {"val": "hello"}},
                {
                    "send": {
                        "topic": "t",
                        "body": "msg.json",
                    },
                },
            ],
        }
        scenario_file = tmp_path / "scenario.yaml"

        scenario_file.write_text(yaml.dump(scenario))

        mock_producer = MagicMock()
        mocker.patch(
            "kafka_emulator.cli.KafkaProducer",
            return_value=mock_producer,
        )

        from kafka_emulator.cli import run_scenario

        run_scenario(str(scenario_file))

        captured = capsys.readouterr()
        assert "[SET]" in captured.out
        assert "val = hello" in captured.out
        assert "[SEND]" in captured.out
        mock_producer.send.assert_called_once()
        sent_body = mock_producer.send.call_args.kwargs["value"]
        parsed = json.loads(sent_body)
        assert parsed["v"] == "hello"

    def test_runs_sleep_and_pause(
        self,
        tmp_path,
        capsys,
        mocker,
    ):
        scenario = {
            "name": "test",
            "kafka": {
                "default": {
                    "bootstrap_servers": "localhost:9092",
                },
            },
            "steps": [
                {"sleep": {"duration": "10ms", "message": "wait"}},
                {"pause": {"timeout": "10ms"}},
            ],
        }
        scenario_file = tmp_path / "scenario.yaml"
        scenario_file.write_text(yaml.dump(scenario))

        mock_producer = MagicMock()
        mocker.patch(
            "kafka_emulator.cli.KafkaProducer",
            return_value=mock_producer,
        )
        mocker.patch("kafka_emulator.cli.wait_for_keypress")

        run_scenario(str(scenario_file))

        captured = capsys.readouterr()
        assert "[SLEEP]" in captured.out
        assert "[PAUSE]" in captured.out

    def test_default_headers_applied(
        self,
        tmp_path,
        capsys,
        mocker,
    ):
        body_file = tmp_path / "msg.txt"
        body_file.write_text("body")

        scenario = {
            "name": "test",
            "kafka": {
                "default": {
                    "bootstrap_servers": "localhost:9092",
                },
            },
            "defaults": {
                "headers": {"x-default": "dval"},
            },
            "steps": [
                {
                    "send": {
                        "topic": "t",
                        "body": "msg.txt",
                    },
                },
            ],
        }
        scenario_file = tmp_path / "scenario.yaml"
        scenario_file.write_text(yaml.dump(scenario))

        mock_producer = MagicMock()
        mocker.patch(
            "kafka_emulator.cli.KafkaProducer",
            return_value=mock_producer,
        )

        run_scenario(str(scenario_file))

        sent_headers = mock_producer.send.call_args.kwargs["headers"]
        header_keys = [h[0] for h in sent_headers]
        assert "x-default" in header_keys

    def test_signal_handler_sets_shutdown(
        self,
        tmp_path,
        capsys,
        mocker,
    ):
        body_file = tmp_path / "msg.txt"
        body_file.write_text("body")

        scenario = {
            "name": "test",
            "kafka": {
                "default": {
                    "bootstrap_servers": "localhost:9092",
                },
            },
            "steps": [
                {"sleep": {"duration": "50ms"}},
                {
                    "send": {
                        "topic": "t",
                        "body": "msg.txt",
                    },
                },
            ],
        }
        scenario_file = tmp_path / "scenario.yaml"
        scenario_file.write_text(yaml.dump(scenario))

        mock_producer = MagicMock()
        mocker.patch(
            "kafka_emulator.cli.KafkaProducer",
            return_value=mock_producer,
        )

        original_sleep = mocker.patch(
            "kafka_emulator.cli.time.sleep",
        )

        def fake_sleep(duration):
            import os

            os.kill(os.getpid(), signal.SIGINT)

        original_sleep.side_effect = fake_sleep

        run_scenario(str(scenario_file))

        captured = capsys.readouterr()
        assert "[SHUTDOWN]" in captured.out
        mock_producer.send.assert_not_called()

    def test_producer_closed_on_error(
        self,
        tmp_path,
        mocker,
    ):
        scenario = {
            "name": "test",
            "kafka": {
                "default": {
                    "bootstrap_servers": "localhost:9092",
                },
            },
            "steps": [
                {
                    "send": {
                        "topic": "t",
                        "body": "nonexistent.json",
                    },
                },
            ],
        }
        scenario_file = tmp_path / "scenario.yaml"
        scenario_file.write_text(yaml.dump(scenario))

        mock_producer = MagicMock()
        mocker.patch(
            "kafka_emulator.cli.KafkaProducer",
            return_value=mock_producer,
        )

        with pytest.raises(FileNotFoundError):
            run_scenario(str(scenario_file))

        mock_producer.flush.assert_called()
        mock_producer.close.assert_called_once()


class TestRunWithScenario:
    def test_run_with_scenario_arg(
        self,
        tmp_path,
        capsys,
        monkeypatch,
        mocker,
    ):
        scenario = {
            "name": "test",
            "kafka": {
                "default": {
                    "bootstrap_servers": "localhost:9092",
                },
            },
            "steps": [{"set": {"x": "1"}}],
        }
        scenario_file = tmp_path / "scenario.yaml"
        scenario_file.write_text(yaml.dump(scenario))

        mock_producer = MagicMock()
        mocker.patch(
            "kafka_emulator.cli.KafkaProducer",
            return_value=mock_producer,
        )
        monkeypatch.setattr(
            "sys.argv",
            ["kafka-emulator", "-s", str(scenario_file)],
        )

        run()

        captured = capsys.readouterr()
        assert "[SET]" in captured.out

    def test_run_with_debug_flag(
        self,
        tmp_path,
        capsys,
        monkeypatch,
        mocker,
    ):
        scenario = {
            "name": "test",
            "kafka": {
                "default": {
                    "bootstrap_servers": "localhost:9092",
                },
            },
            "steps": [{"set": {"x": "1"}}],
        }
        scenario_file = tmp_path / "scenario.yaml"
        scenario_file.write_text(yaml.dump(scenario))

        mock_producer = MagicMock()
        mocker.patch(
            "kafka_emulator.cli.KafkaProducer",
            return_value=mock_producer,
        )
        monkeypatch.setattr(
            "sys.argv",
            [
                "kafka-emulator",
                "--debug",
                "-s",
                str(scenario_file),
            ],
        )

        run()

    def test_run_with_log_level(
        self,
        tmp_path,
        capsys,
        monkeypatch,
        mocker,
    ):
        scenario = {
            "name": "test",
            "kafka": {
                "default": {
                    "bootstrap_servers": "localhost:9092",
                },
            },
            "steps": [{"set": {"x": "1"}}],
        }
        scenario_file = tmp_path / "scenario.yaml"
        scenario_file.write_text(yaml.dump(scenario))

        mock_producer = MagicMock()
        mocker.patch(
            "kafka_emulator.cli.KafkaProducer",
            return_value=mock_producer,
        )
        monkeypatch.setattr(
            "sys.argv",
            [
                "kafka-emulator",
                "--log-level",
                "WARNING",
                "-s",
                str(scenario_file),
            ],
        )

        run()

    def test_run_scenario_error_prints_stderr(
        self,
        monkeypatch,
        capsys,
        mocker,
    ):
        mocker.patch(
            "kafka_emulator.cli.run_scenario",
            side_effect=RuntimeError("fail"),
        )
        monkeypatch.setattr(
            "sys.argv",
            ["kafka-emulator", "-s", "bad.yaml"],
        )

        with pytest.raises(SystemExit) as exc:
            run()
        assert exc.value.code == 1
        captured = capsys.readouterr()
        assert "Error: fail" in captured.err


class TestWaitForKeypressTty:
    def test_tty_with_timeout_termios(self, mocker):
        mocker.patch("sys.stdin.isatty", return_value=True)
        mocker.patch(
            "sys.stdin.fileno",
            return_value=0,
        )
        mock_termios = MagicMock()
        mock_termios.tcgetattr.return_value = [0]
        mock_tty = MagicMock()
        mocker.patch.dict(
            "sys.modules",
            {"termios": mock_termios, "tty": mock_tty},
        )
        mocker.patch(
            "kafka_emulator.cli.select.select",
            return_value=([], [], []),
        )

        wait_for_keypress(0.01)

        mock_tty.setraw.assert_called_once()
        mock_termios.tcsetattr.assert_called_once()

    def test_tty_no_timeout_termios(self, mocker):
        mocker.patch("sys.stdin.isatty", return_value=True)
        mocker.patch("sys.stdin.fileno", return_value=0)
        mocker.patch("sys.stdin.read", return_value="x")
        mock_termios = MagicMock()
        mock_termios.tcgetattr.return_value = [0]
        mock_tty = MagicMock()
        mocker.patch.dict(
            "sys.modules",
            {"termios": mock_termios, "tty": mock_tty},
        )

        wait_for_keypress(None)

    def test_tty_fallback_on_import_error(self, mocker):
        mocker.patch("sys.stdin.isatty", return_value=True)

        mock_sleep = mocker.patch(
            "kafka_emulator.cli.time.sleep",
        )

        mocker.patch("sys.stdin.isatty", return_value=True)
        mocker.patch(
            "sys.stdin.fileno",
            side_effect=OSError("no fd"),
        )

        wait_for_keypress(0.01)
        mock_sleep.assert_called_with(0.01)

    def test_tty_fallback_input_no_timeout(self, mocker):
        mocker.patch("sys.stdin.isatty", return_value=True)
        mocker.patch(
            "sys.stdin.fileno",
            side_effect=OSError("no fd"),
        )
        mock_input = mocker.patch("builtins.input")

        wait_for_keypress(None)
        mock_input.assert_called_once()
