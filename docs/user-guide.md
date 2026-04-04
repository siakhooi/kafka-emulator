# User Guide

## Overview

`kafka-emulator` is a command-line tool for sending messages to Kafka topics
using scenario files. Scenarios are defined in YAML and support Jinja2
templates for dynamic content generation.

## Installation

```bash
pip install kafka_emulator
```

## Quick Start

1. Create a scenario file `scenario.yaml`:

```yaml
name: Hello World

kafka:
  default:
    bootstrap_servers: "localhost:9092"

steps:
  - send:
      topic: "test-topic"
      body: "message.json"
```

2. Create a message body file `message.json`:

```json
{
    "greeting": "Hello, World!",
    "timestamp": "{{ now() }}"
}
```

3. Run the scenario:

```bash
kafka-emulator -s scenario.yaml
```

## Command-Line Options

```
kafka-emulator [-h] [-v] [-s SCENARIO] [--debug]
               [--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
```

| Option | Description |
|--------|-------------|
| `-h`, `--help` | Show help message and exit |
| `-v`, `--version` | Show version and exit |
| `-s`, `--scenario SCENARIO` | Path to scenario YAML file |
| `--debug` | Enable debug logging (shortcut for `--log-level DEBUG`) |
| `--log-level LEVEL` | Set log level: `DEBUG`, `INFO` (default), `WARNING`, `ERROR`, `CRITICAL` |

## Writing Scenarios

A scenario file defines a sequence of steps to execute. All file paths
in the scenario (such as message body files) are relative to the scenario
file's directory.

See [Scenario YAML Specification](scenario-spec.md) for the full reference.

### Setting Variables

Use `set` steps to define variables for use in later steps:

```yaml
steps:
  - set:
      user_id: "{{ uuid() }}"
      start_time: "{{ now() }}"
```

Variables are available in all subsequent step templates as `{{ user_id }}`,
`{{ start_time }}`, etc.

### Sending Messages

Use `send` steps to publish messages to Kafka topics:

```yaml
steps:
  - send:
      topic: "orders"
      key: "{{ user_id }}"
      body: "order.json"
      headers:
        content-type: application/json
        x-request-id: "{{ uuid() }}"
```

The `body` field points to a file whose contents are rendered as a Jinja2
template. If the rendered body is valid JSON, it is automatically minified
before sending.

### Default Headers

Define headers that apply to all `send` steps:

```yaml
defaults:
  headers:
    content-type: application/json
    x-source: kafka-emulator
```

Step-level headers override default headers when they share the same key.

### Adding Delays

Use `sleep` to pause between steps:

```yaml
- sleep:
    message: "Waiting for processing"
    duration: 2s
```

Supported duration units: `ms` (milliseconds, default), `s` (seconds),
`m` (minutes), `h` (hours).

### Waiting for User Input

Use `pause` to wait for a keypress:

```yaml
# Wait indefinitely for a keypress
- pause:
    message: "Press any key to continue"

# Wait with a timeout
- pause:
    message: "Waiting for verification"
    timeout: 10s
```

If running in a non-interactive environment (e.g., piped input), `pause`
with a timeout behaves like `sleep`, and `pause` without a timeout is
skipped.

## Template Helpers

All string values in steps support Jinja2 templates. The following helper
functions are available:

### Date and Time

| Function | Example | Description |
|----------|---------|-------------|
| `now()` | `{{ now() }}` | Current datetime in ISO 8601 |
| `today()` | `{{ today() }}` | Current date in ISO 8601 |
| `epoch()` | `{{ epoch() }}` | Unix timestamp in seconds |
| `epoch_ms()` | `{{ epoch_ms() }}` | Unix timestamp in milliseconds |
| `date_add(base, ...)` | `{{ date_add(now(), days=1) }}` | Add time offset to a datetime |
| `dt_format(value, fmt)` | `{{ dt_format(now(), '%Y-%m-%d') }}` | Format a datetime string |

#### `date_add` Examples

```
{{ date_add(now(), hours=2) }}
{{ date_add(now(), days=-1) }}
{{ date_add(now(), weeks=1, hours=12) }}
```

### Identifiers and Randomness

| Function | Example | Description |
|----------|---------|-------------|
| `uuid()` | `{{ uuid() }}` | Generate a UUID v4 |
| `seq()` | `{{ seq() }}` | Auto-incrementing counter (default name) |
| `seq('name')` | `{{ seq('order') }}` | Named auto-incrementing counter |
| `random_string(n)` | `{{ random_string(16) }}` | Random alphanumeric string |
| `randint(a, b)` | `{{ randint(1, 1000) }}` | Random integer in [a, b] |
| `choice(list)` | `{{ choice(['a','b','c']) }}` | Random pick from list |

#### `seq` Examples

Each named counter starts at 0 and increments by 1 on each call:

```yaml
steps:
  - send:
      topic: "events"
      body: "event.json"
      headers:
        x-seq: "{{ seq() }}"          # 1
        x-order-seq: "{{ seq('order') }}" # 1
  - send:
      topic: "events"
      body: "event.json"
      headers:
        x-seq: "{{ seq() }}"          # 2
        x-order-seq: "{{ seq('order') }}" # 2
```

### Encoding and Hashing

| Function | Example | Description |
|----------|---------|-------------|
| `b64encode(value)` | `{{ b64encode('hello') }}` | Base64 encode |
| `b64decode(value)` | `{{ b64decode('aGVsbG8=') }}` | Base64 decode |
| `md5(value)` | `{{ md5('data') }}` | MD5 hash (hex) |
| `sha256(value)` | `{{ sha256('data') }}` | SHA-256 hash (hex) |
| `urlencode(value)` | `{{ urlencode('a b') }}` | URL percent-encode |
| `urldecode(value)` | `{{ urldecode('a%20b') }}` | URL percent-decode |

## Console Output

Each step prints a colored, prefixed message to the console:

| Prefix | Color | Step Type |
|--------|-------|-----------|
| `[SET]` | Cyan | Variable assignment |
| `[SEND]` | Green | Message sent to Kafka |
| `[SLEEP]` | Yellow | Sleep/delay |
| `[PAUSE]` | Magenta | Waiting for keypress |
| `[SHUTDOWN]` | Yellow | Graceful shutdown triggered |

Example output:

```
[SET] user_id = f04acb56-afec-4150-8b73-b5405eb90162
[SET] order_id = 155d1824-a771-41a1-8932-1eca831e9416
[SEND] Sent message to topic 'orders' with key 'f04acb56-...'
[SLEEP] Waiting 500ms
[PAUSE] Press any key (timeout: 5s)...
```

## Logging

Structured log messages are written to stderr. Use `--debug` or
`--log-level` to control verbosity:

```bash
# Normal operation (INFO level, default)
kafka-emulator -s scenario.yaml

# Debug logging
kafka-emulator -s scenario.yaml --debug

# Only warnings and errors
kafka-emulator -s scenario.yaml --log-level WARNING
```

## Graceful Shutdown

The program handles `SIGINT` (Ctrl+C) and `SIGTERM` gracefully:

1. Stops processing further steps
2. Flushes any pending Kafka messages
3. Closes the Kafka producer
4. Exits cleanly

## Complete Example

**scenario.yaml:**

```yaml
name: E-Commerce Order Flow

kafka:
  default:
    bootstrap_servers: "localhost:9092"

defaults:
  headers:
    content-type: application/json
    x-source: kafka-emulator

steps:
  - set:
      user_id: "{{ uuid() }}"
      order_id: "{{ uuid() }}"
      order_date: "{{ now() }}"

  - send:
      topic: "orders"
      key: "{{ order_id }}"
      body: "order-created.json"
      headers:
        x-correlation-id: "{{ uuid() }}"
        x-seq: "{{ seq() }}"

  - sleep:
      message: "Simulating processing delay"
      duration: 1s

  - send:
      topic: "orders"
      key: "{{ order_id }}"
      body: "order-confirmed.json"
      headers:
        x-seq: "{{ seq() }}"

  - pause:
      message: "Verify order in consumer"
      timeout: 10s

  - send:
      topic: "notifications"
      body: "notification.json"
      headers:
        x-seq: "{{ seq() }}"
```

**order-created.json:**

```json
{
    "event": "order_created",
    "order_id": "{{ order_id }}",
    "user_id": "{{ user_id }}",
    "order_date": "{{ order_date }}",
    "total": {{ randint(100, 9999) }},
    "checksum": "{{ sha256(order_id) }}"
}
```
