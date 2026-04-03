import re


def parse_duration(duration_str: str) -> float:
    """Parse duration string (e.g., '500ms', '1s', '2m') to seconds."""
    match = re.match(r"^(\d+(?:\.\d+)?)\s*(ms|s|m|h)?$", duration_str.strip())
    if not match:
        raise ValueError(f"Invalid duration format: {duration_str}")

    value = float(match.group(1))
    unit = match.group(2) or "ms"

    if unit == "ms":
        return value / 1000
    elif unit == "s":
        return value
    elif unit == "m":
        return value * 60
    else:  # unit == "h"
        return value * 3600
