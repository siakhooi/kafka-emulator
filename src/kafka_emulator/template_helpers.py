import datetime
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


def get_template_helpers() -> dict[str, callable]:
    """Return the map of template helper names to callable functions."""
    return {
        "uuid": generate_uuid,
        "now": now,
        "epoch": epoch,
    }
