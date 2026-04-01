import argparse
import re
import sys
import time
from importlib.metadata import version
from pathlib import Path

import yaml
from kafka import KafkaProducer


def print_to_stderr_and_exit(e: Exception, exit_code: int) -> None:
    print(f"Error: {e}", file=sys.stderr)
    exit(exit_code)


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
    elif unit == "h":
        return value * 3600
    return value / 1000


def run_scenario(scenario_path: str) -> None:
    """Run a scenario from a YAML file."""
    scenario_dir = Path(scenario_path).parent

    with open(scenario_path, "r") as f:
        scenario = yaml.safe_load(f)

    kafka_config = scenario.get("kafka", {}).get("default", {})
    bootstrap_servers = kafka_config.get("bootstrap_servers", "localhost:9092")

    producer = KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        key_serializer=lambda k: k.encode("utf-8") if k else None,
        value_serializer=lambda v: (
            v.encode("utf-8") if isinstance(v, str) else v
        ),
    )

    try:
        steps = scenario.get("steps", [])
        for step in steps:
            if "send" in step:
                send_config = step["send"]
                topic = send_config.get("topic")
                key = send_config.get("key")
                headers_dict = send_config.get("headers", {})
                body_file = send_config.get("body")

                body_path = scenario_dir / body_file
                with open(body_path, "r") as f:
                    body = f.read()

                headers = None
                if headers_dict:
                    headers = [
                        (k, v.encode("utf-8")) for k, v in headers_dict.items()
                    ]

                producer.send(
                    topic=topic,
                    key=key,
                    value=body,
                    headers=headers,
                )
                producer.flush()
                print(f"Sent message to topic '{topic}' with key '{key}'")

            elif "sleep" in step:
                sleep_config = step["sleep"]
                message = sleep_config.get("message")
                duration_str = sleep_config.get("duration", "0ms")

                if message:
                    print(message)

                duration_seconds = parse_duration(duration_str)
                time.sleep(duration_seconds)

    finally:
        producer.close()


def run() -> None:
    __version__: str = version("kafka-emulator")

    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Kafka Messages Emulator"
    )

    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {__version__}"
    )

    parser.add_argument(
        "-s", "--scenario",
        type=str,
        help="Path to scenario YAML file"
    )

    args = parser.parse_args()

    if args.scenario:
        try:
            run_scenario(args.scenario)
        except Exception as e:
            print_to_stderr_and_exit(e, 1)
