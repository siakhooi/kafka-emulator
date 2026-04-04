import argparse
import datetime
import json
import re
import select
import sys
import time
import uuid
from importlib.metadata import version
from pathlib import Path

import yaml
from jinja2 import Template
from kafka import KafkaProducer

from kafka_emulator.template_helpers import get_template_helpers
from kafka_emulator.duration import parse_duration


def print_to_stderr_and_exit(e: Exception, exit_code: int) -> None:
    print(f"Error: {e}", file=sys.stderr)
    exit(exit_code)


def wait_for_keypress(timeout: float | None) -> None:
    """Wait for a keypress with optional timeout."""
    if not sys.stdin.isatty():
        if timeout:
            time.sleep(timeout)
        return

    try:
        import termios
        import tty

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            if timeout:
                ready, _, _ = select.select([sys.stdin], [], [], timeout)
                if ready:
                    sys.stdin.read(1)
            else:
                sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            print()
    except (ImportError, OSError):
        if timeout:
            time.sleep(timeout)
        else:
            input()


def render_template(value: str, context: dict) -> str:
    """Render a string value as a Jinja template using the context."""
    if value is None:
        return None
    template = Template(str(value))
    render_context = {**context, **get_template_helpers()}
    return template.render(**render_context)


def run_scenario(scenario_path: str) -> None:
    """Run a scenario from a YAML file."""
    scenario_dir = Path(scenario_path).parent

    with open(scenario_path, "r") as f:
        scenario = yaml.safe_load(f)

    scenario_name = scenario.get("name", "unnamed")
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    run_datetime = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
    scenario_name_normalized = re.sub(
        r"[^a-z0-9]+", "_", scenario_name.lower()
    ).strip("_")
    run_datetime_short = now_utc.strftime("%Y%m%d_%H%M%S")
    run_name = f"{scenario_name_normalized}_{run_datetime_short}"
    run_id = str(uuid.uuid4())

    context = {
        "scenario_name": scenario_name,
        "run_name": run_name,
        "run_datetime": run_datetime,
        "run_id": run_id,
    }

    defaults = scenario.get("defaults", {})
    default_headers = defaults.get("headers", {})

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
            if "set" in step:
                set_config = step["set"]
                if set_config:
                    for key, value in set_config.items():
                        rendered_value = render_template(str(value), context)
                        context[key] = rendered_value

            elif "send" in step:
                send_config = step["send"]
                topic = send_config.get("topic")
                key = send_config.get("key")
                if key is not None:
                    key = render_template(str(key), context)
                step_headers = send_config.get("headers", {})
                headers_dict = {**default_headers, **step_headers}
                body_file = send_config.get("body")

                body_path = scenario_dir / body_file
                with open(body_path, "r") as f:
                    body_content = f.read()
                body = render_template(body_content, context)

                try:
                    body = json.dumps(json.loads(body), separators=(",", ":"))
                except (json.JSONDecodeError, ValueError):
                    pass

                headers = None
                if headers_dict:
                    headers = [
                        (k, render_template(str(v), context).encode("utf-8"))
                        for k, v in headers_dict.items()
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
                if message:
                    message = render_template(str(message), context)
                duration_str = sleep_config.get("duration", "0ms")

                if message:
                    print(message)

                duration_seconds = parse_duration(duration_str)
                time.sleep(duration_seconds)

            elif "pause" in step:
                pause_config = step["pause"]
                message = pause_config.get("message")
                if message:
                    message = render_template(str(message), context)
                timeout_str = pause_config.get("timeout")

                if message:
                    print(message)

                if timeout_str:
                    timeout_seconds = parse_duration(timeout_str)
                    print(f"Press any key (timeout: {timeout_str})...")
                    wait_for_keypress(timeout_seconds)
                else:
                    print("Press any key to continue...")
                    wait_for_keypress(None)

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
        "-s", "--scenario", type=str, help="Path to scenario YAML file"
    )

    args = parser.parse_args()

    if args.scenario:
        try:
            run_scenario(args.scenario)
        except Exception as e:
            print_to_stderr_and_exit(e, 1)
