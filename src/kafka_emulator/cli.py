import argparse
import sys
from importlib.metadata import version


def print_to_stderr_and_exit(e: Exception, exit_code: int) -> None:
    print(f"Error: {e}", file=sys.stderr)
    exit(exit_code)


def run() -> None:
    __version__: str = version("kafka-emulator")

    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Kafka Messages Emulator"
    )

    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {__version__}"
    )

    parser.parse_args()
