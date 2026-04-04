import datetime
import random
import uuid

import pytest

from kafka_emulator.template_helpers import (
    _seq_counters,
    b64decode,
    b64encode,
    date_add,
    dt_format,
    epoch,
    epoch_ms,
    generate_uuid,
    get_template_helpers,
    md5,
    now,
    random_string,
    seq,
    sha256,
    today,
    urldecode,
    urlencode,
)


class TestGenerateUuid:
    def test_returns_valid_uuid(self):
        result = generate_uuid()
        parsed = uuid.UUID(result)
        assert str(parsed) == result

    def test_returns_unique_values(self):
        assert generate_uuid() != generate_uuid()


class TestNow:
    def test_returns_iso_format(self):
        result = now()
        parsed = datetime.datetime.fromisoformat(result)
        assert isinstance(parsed, datetime.datetime)

    def test_returns_current_time(self):
        before = datetime.datetime.now()
        result = datetime.datetime.fromisoformat(now())
        after = datetime.datetime.now()
        assert before <= result <= after


class TestToday:
    def test_returns_iso_date(self):
        result = today()
        parsed = datetime.date.fromisoformat(result)
        assert parsed == datetime.date.today()


class TestEpoch:
    def test_returns_int(self):
        result = epoch()
        assert isinstance(result, int)

    def test_returns_current_timestamp(self):
        before = int(datetime.datetime.now().timestamp())
        result = epoch()
        after = int(datetime.datetime.now().timestamp())
        assert before <= result <= after


class TestEpochMs:
    def test_returns_int(self):
        result = epoch_ms()
        assert isinstance(result, int)

    def test_returns_milliseconds(self):
        result = epoch_ms()
        assert result > epoch() * 999


class TestDateAdd:
    def test_with_string_base(self):
        result = date_add("2026-01-01T00:00:00", days=1)
        assert result == "2026-01-02T00:00:00"

    def test_with_datetime_base(self):
        base = datetime.datetime(2026, 1, 1)
        result = date_add(base, hours=2)
        assert result == "2026-01-01T02:00:00"

    def test_weeks(self):
        result = date_add("2026-01-01T00:00:00", weeks=1)
        assert result == "2026-01-08T00:00:00"

    def test_negative_offset(self):
        result = date_add("2026-01-10T00:00:00", days=-3)
        assert result == "2026-01-07T00:00:00"

    def test_combined_offsets(self):
        result = date_add(
            "2026-01-01T00:00:00",
            days=1,
            hours=2,
            minutes=30,
            seconds=15,
        )
        assert result == "2026-01-02T02:30:15"


class TestDtFormat:
    def test_with_string(self):
        result = dt_format("2026-04-04T09:30:00", "%Y-%m-%d")
        assert result == "2026-04-04"

    def test_with_datetime(self):
        dt = datetime.datetime(2026, 4, 4, 9, 30)
        result = dt_format(dt, "%H:%M")
        assert result == "09:30"

    def test_custom_format(self):
        result = dt_format("2026-12-25T00:00:00", "%d/%m/%Y")
        assert result == "25/12/2026"


class TestRandomString:
    def test_default_length(self):
        result = random_string()
        assert len(result) == 8

    def test_custom_length(self):
        result = random_string(16)
        assert len(result) == 16

    def test_alphanumeric_only(self):
        allowed = set(
            "abcdefghijklmnopqrstuvwxyz"
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            "0123456789"
        )
        result = random_string(100)
        assert all(c in allowed for c in result)

    def test_zero_length(self):
        assert random_string(0) == ""


class TestB64Encode:
    def test_encode(self):
        assert b64encode("hello") == "aGVsbG8="

    def test_empty(self):
        assert b64encode("") == ""

    def test_unicode(self):
        result = b64encode("café")
        assert b64decode(result) == "café"


class TestB64Decode:
    def test_decode(self):
        assert b64decode("aGVsbG8=") == "hello"

    def test_empty(self):
        assert b64decode("") == ""


class TestMd5:
    def test_known_hash(self):
        assert md5("hello") == "5d41402abc4b2a76b9719d911017c592"

    def test_empty(self):
        assert md5("") == "d41d8cd98f00b204e9800998ecf8427e"


class TestSha256:
    def test_known_hash(self):
        result = sha256("hello")
        assert result == (
            "2cf24dba5fb0a30e26e83b2ac5b9e29e"
            "1b161e5c1fa7425e73043362938b9824"
        )

    def test_empty(self):
        result = sha256("")
        assert result == (
            "e3b0c44298fc1c149afbf4c8996fb924"
            "27ae41e4649b934ca495991b7852b855"
        )


class TestUrlencode:
    def test_spaces(self):
        assert urlencode("a b") == "a%20b"

    def test_special_chars(self):
        assert urlencode("a&b=c") == "a%26b%3Dc"

    def test_no_encoding_needed(self):
        assert urlencode("hello") == "hello"


class TestUrldecode:
    def test_spaces(self):
        assert urldecode("a%20b") == "a b"

    def test_special_chars(self):
        assert urldecode("a%26b%3Dc") == "a&b=c"

    def test_no_decoding_needed(self):
        assert urldecode("hello") == "hello"


class TestSeq:
    @pytest.fixture(autouse=True)
    def reset_counters(self):
        _seq_counters.clear()
        yield
        _seq_counters.clear()

    def test_default_counter(self):
        assert seq() == 1
        assert seq() == 2
        assert seq() == 3

    def test_named_counter(self):
        assert seq("a") == 1
        assert seq("a") == 2
        assert seq("b") == 1
        assert seq("a") == 3

    def test_default_name(self):
        seq()
        assert _seq_counters["default"] == 1


class TestGetTemplateHelpers:
    def test_returns_dict(self):
        helpers = get_template_helpers()
        assert isinstance(helpers, dict)

    def test_all_helpers_present(self):
        helpers = get_template_helpers()
        expected = [
            "uuid",
            "now",
            "epoch",
            "epoch_ms",
            "today",
            "date_add",
            "randint",
            "choice",
            "random_string",
            "b64encode",
            "b64decode",
            "md5",
            "sha256",
            "urlencode",
            "urldecode",
            "dt_format",
            "seq",
        ]
        for name in expected:
            assert name in helpers, f"Missing helper: {name}"

    def test_all_values_callable(self):
        helpers = get_template_helpers()
        for name, func in helpers.items():
            assert callable(func), f"{name} is not callable"

    def test_randint_is_random_randint(self):
        helpers = get_template_helpers()
        assert helpers["randint"] is random.randint

    def test_choice_is_random_choice(self):
        helpers = get_template_helpers()
        assert helpers["choice"] is random.choice
