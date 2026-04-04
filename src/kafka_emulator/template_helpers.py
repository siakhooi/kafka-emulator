import base64
import datetime
import hashlib
import random
import uuid


def generate_uuid() -> str:
    """Return a new UUID string."""
    return str(uuid.uuid4())


def now() -> str:
    """Return the current date/time in ISO 8601 format."""
    return datetime.datetime.now().isoformat()


def today() -> str:
    """Return the current date in ISO 8601 format."""
    return datetime.date.today().isoformat()


def epoch() -> int:
    """Return the current time as a Unix timestamp."""
    return int(datetime.datetime.now().timestamp())


def epoch_ms() -> int:
    """Return the current time as a Unix timestamp in milliseconds."""
    return int(datetime.datetime.now().timestamp() * 1000)


def date_add(
    base: datetime.datetime | str,
    weeks: int = 0,
    days: int = 0,
    hours: int = 0,
    minutes: int = 0,
    seconds: int = 0,
) -> str:
    """Return a new datetime with the specified offset."""
    if isinstance(base, str):
        base = datetime.datetime.fromisoformat(base)
    result = base + datetime.timedelta(
        weeks=weeks, days=days, hours=hours, minutes=minutes, seconds=seconds
    )
    return result.isoformat()


def random_string(length: int = 8) -> str:
    """Return a random string of the specified length."""
    letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return "".join(random.choice(letters) for _ in range(length))


def b64encode(value: str) -> str:
    """Return the base64-encoded version of the input string."""
    return base64.b64encode(value.encode("utf-8")).decode("utf-8")


def b64decode(value: str) -> str:
    """Return the base64-decoded version of the input string."""
    return base64.b64decode(value).decode("utf-8")


def md5(value: str) -> str:
    """Return the MD5 hash of the input string."""
    return hashlib.md5(value.encode("utf-8")).hexdigest()


def sha256(value: str) -> str:
    """Return the SHA-256 hash of the input string."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def get_template_helpers() -> dict[str, callable]:
    """Return the map of template helper names to callable functions."""
    return {
        "uuid": generate_uuid,
        "now": now,
        "epoch": epoch,
        "epoch_ms": epoch_ms,
        "today": today,
        "date_add": date_add,
        "randint": random.randint,
        "choice": random.choice,
        "random_string": random_string,
        "b64encode": b64encode,
        "b64decode": b64decode,
        "md5": md5,
        "sha256": sha256,
    }
