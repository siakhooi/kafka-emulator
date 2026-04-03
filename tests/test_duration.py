import pytest

from kafka_emulator.duration import parse_duration


class TestParseDuration:
    """Tests for parse_duration function."""

    def test_milliseconds(self):
        assert parse_duration("500ms") == 0.5
        assert parse_duration("1000ms") == 1.0
        assert parse_duration("100ms") == 0.1

    def test_seconds(self):
        assert parse_duration("1s") == 1.0
        assert parse_duration("5s") == 5.0
        assert parse_duration("10s") == 10.0

    def test_minutes(self):
        assert parse_duration("1m") == 60.0
        assert parse_duration("2m") == 120.0
        assert parse_duration("5m") == 300.0

    def test_hours(self):
        assert parse_duration("1h") == 3600.0
        assert parse_duration("2h") == 7200.0

    def test_decimal_values(self):
        assert parse_duration("1.5s") == 1.5
        assert parse_duration("0.5m") == 30.0
        assert parse_duration("2.5h") == 9000.0

    def test_default_unit_is_milliseconds(self):
        assert parse_duration("500") == 0.5
        assert parse_duration("1000") == 1.0

    def test_whitespace_handling(self):
        assert parse_duration("  500ms  ") == 0.5
        assert parse_duration("1 s") == 1.0

    def test_invalid_format_raises_error(self):
        with pytest.raises(ValueError, match="Invalid duration format"):
            parse_duration("invalid")

    def test_empty_string_raises_error(self):
        with pytest.raises(ValueError, match="Invalid duration format"):
            parse_duration("")

    def test_negative_value_raises_error(self):
        with pytest.raises(ValueError, match="Invalid duration format"):
            parse_duration("-5s")
