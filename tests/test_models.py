import pytest
from pydantic import ValidationError

from kafka_emulator.models import (
    Defaults,
    KafkaConfig,
    KafkaDefault,
    PauseStep,
    Scenario,
    SendStep,
    SleepStep,
    Step,
)


class TestKafkaDefault:
    def test_defaults(self):
        k = KafkaDefault()
        assert k.bootstrap_servers == "localhost:9092"

    def test_custom(self):
        k = KafkaDefault(bootstrap_servers="broker:9093")
        assert k.bootstrap_servers == "broker:9093"


class TestKafkaConfig:
    def test_defaults(self):
        c = KafkaConfig()
        assert c.default.bootstrap_servers == "localhost:9092"

    def test_custom(self):
        c = KafkaConfig(default={"bootstrap_servers": "broker:9093"})
        assert c.default.bootstrap_servers == "broker:9093"


class TestDefaults:
    def test_defaults(self):
        d = Defaults()
        assert d.headers == {}

    def test_custom_headers(self):
        d = Defaults(headers={"content-type": "application/json"})
        assert d.headers == {"content-type": "application/json"}


class TestSendStep:
    def test_required_fields(self):
        s = SendStep(topic="t", body="b.json")
        assert s.topic == "t"
        assert s.body == "b.json"
        assert s.key is None
        assert s.headers == {}

    def test_all_fields(self):
        s = SendStep(
            topic="t",
            body="b.json",
            key="k",
            headers={"h": "v"},
        )
        assert s.key == "k"
        assert s.headers == {"h": "v"}

    def test_missing_topic(self):
        with pytest.raises(ValidationError):
            SendStep(body="b.json")

    def test_missing_body(self):
        with pytest.raises(ValidationError):
            SendStep(topic="t")


class TestSleepStep:
    def test_defaults(self):
        s = SleepStep()
        assert s.message is None
        assert s.duration == "0ms"

    def test_custom(self):
        s = SleepStep(message="wait", duration="5s")
        assert s.message == "wait"
        assert s.duration == "5s"


class TestPauseStep:
    def test_defaults(self):
        p = PauseStep()
        assert p.message is None
        assert p.timeout is None

    def test_custom(self):
        p = PauseStep(message="pause", timeout="10s")
        assert p.message == "pause"
        assert p.timeout == "10s"


class TestStep:
    def test_set_step(self):
        s = Step(set={"k": "v"})
        assert s.set == {"k": "v"}
        assert s.send is None
        assert s.sleep is None
        assert s.pause is None

    def test_send_step(self):
        s = Step(send={"topic": "t", "body": "b.json"})
        assert s.send.topic == "t"

    def test_sleep_step(self):
        s = Step(sleep={"duration": "1s"})
        assert s.sleep.duration == "1s"

    def test_pause_step(self):
        s = Step(pause={"timeout": "5s"})
        assert s.pause.timeout == "5s"

    def test_no_step_raises(self):
        with pytest.raises(ValidationError, match="exactly one"):
            Step()

    def test_multiple_steps_raises(self):
        with pytest.raises(ValidationError, match="exactly one"):
            Step(
                set={"k": "v"},
                send={"topic": "t", "body": "b.json"},
            )


class TestScenario:
    def test_minimal(self):
        s = Scenario(steps=[{"set": {"k": "v"}}])
        assert s.name == "unnamed"
        assert s.kafka.default.bootstrap_servers == "localhost:9092"
        assert s.defaults.headers == {}
        assert len(s.steps) == 1

    def test_full(self):
        s = Scenario(
            name="test",
            kafka={"default": {"bootstrap_servers": "b:9093"}},
            defaults={"headers": {"h": "v"}},
            steps=[
                {"set": {"a": "1"}},
                {"send": {"topic": "t", "body": "b.json"}},
                {"sleep": {"duration": "1s"}},
                {"pause": {"timeout": "5s"}},
            ],
        )
        assert s.name == "test"
        assert s.kafka.default.bootstrap_servers == "b:9093"
        assert s.defaults.headers == {"h": "v"}
        assert len(s.steps) == 4

    def test_missing_steps_raises(self):
        with pytest.raises(ValidationError):
            Scenario()

    def test_empty_steps(self):
        s = Scenario(steps=[])
        assert s.steps == []

    def test_invalid_step_raises(self):
        with pytest.raises(ValidationError):
            Scenario(steps=[{"send": {"topic": "t"}}])
