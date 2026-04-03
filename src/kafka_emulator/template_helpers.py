import datetime
import random
import uuid


def generate_uuid() -> str:
    """Return a new UUID string."""
    return str(uuid.uuid4())


def now() -> str:
    """Return the current date/time in ISO 8601 format."""
    return datetime.datetime.now().isoformat()


def epoch() -> int:
    """Return the current time as a Unix timestamp."""
    return int(datetime.datetime.now().timestamp())


def epoch_ms() -> int:
    """Return the current time as a Unix timestamp in milliseconds."""
    return int(datetime.datetime.now().timestamp() * 1000)


def random_string(length: int = 8) -> str:
    """Return a random string of the specified length."""
    letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return "".join(random.choice(letters) for _ in range(length))


def get_template_helpers() -> dict[str, callable]:
    """Return the map of template helper names to callable functions."""
    return {
        "uuid": generate_uuid,
        "now": now,
        "epoch": epoch,
        "epoch_ms": epoch_ms,
        "randint": random.randint,
        "choice": random.choice,
        "random_string": random_string,
    }
