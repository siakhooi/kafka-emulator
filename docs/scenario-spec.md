# Scenario YAML Specification

This document describes the structure and syntax of the scenario YAML file
used by `kafka-emulator`.

## Top-Level Structure

```yaml
name: <string>

kafka:
  default:
    bootstrap_servers: <string>

defaults:
  headers:
    <key>: <value>

steps:
  - <step>
  - <step>
  ...
```

### Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `name` | string | No | `unnamed` | Name of the scenario. Used to generate `run_name`. |
| `kafka` | object | No | See below | Kafka connection configuration. |
| `defaults` | object | No | See below | Default values applied to all steps. |
| `steps` | list | **Yes** | | Ordered list of steps to execute. |

---

## `kafka`

```yaml
kafka:
  default:
    bootstrap_servers: "localhost:9092"
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `kafka.default.bootstrap_servers` | string | No | `localhost:9092` | Kafka broker address. |

---

## `defaults`

```yaml
defaults:
  headers:
    content-type: application/json
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `defaults.headers` | map | No | `{}` | Headers applied to all `send` steps. Step-level headers with the same key override these. |

---

## Steps

Each step is a single-key object. Exactly one of the following step types
must be specified per list entry: `set`, `send`, `sleep`, `pause`.

### `set`

Define or update context variables. Values support Jinja2 templates.

```yaml
- set:
    user_id: "{{ uuid() }}"
    order_date: "{{ now() }}"
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `set` | map of string to string | **Yes** | Key-value pairs to set in the context. Values are rendered as Jinja2 templates. |

### `send`

Send a message to a Kafka topic.

```yaml
- send:
    topic: "my-topic"
    body: "message.json"
    key: "{{ user_id }}"
    headers:
      x-request-id: "{{ uuid() }}"
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `topic` | string | **Yes** | | Kafka topic to send the message to. |
| `body` | string | **Yes** | | Path to the message body file, relative to the scenario file directory. The file content is rendered as a Jinja2 template. If the rendered content is valid JSON, it is minified before sending. |
| `key` | string | No | `None` | Message key. Rendered as a Jinja2 template. |
| `headers` | map | No | `{}` | Message headers. Values are rendered as Jinja2 templates. Merged with `defaults.headers`; step-level headers take precedence on key conflicts. |

### `sleep`

Pause execution for a specified duration.

```yaml
- sleep:
    message: "Waiting 500ms"
    duration: 500ms
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `message` | string | No | `None` | Message to display. Rendered as a Jinja2 template. |
| `duration` | string | No | `0ms` | Duration to sleep. See [Duration Format](#duration-format). |

### `pause`

Wait for user keypress, with optional timeout.

```yaml
- pause:
    message: "Waiting for processing"
    timeout: 5s
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `message` | string | No | `None` | Message to display. Rendered as a Jinja2 template. |
| `timeout` | string | No | `None` | Timeout duration. If not set, waits indefinitely. See [Duration Format](#duration-format). |

---

## Duration Format

Duration strings consist of a number followed by a unit:

| Unit | Description | Example |
|------|-------------|---------|
| `ms` | Milliseconds (default) | `500ms` |
| `s` | Seconds | `5s` |
| `m` | Minutes | `2m` |
| `h` | Hours | `1h` |

If no unit is specified, `ms` is assumed.

---

## Template Context

All string values in steps are rendered as [Jinja2](https://jinja.palletsprojects.com/) templates.

### Built-in Context Variables

These variables are automatically available in all templates:

| Variable | Description | Example |
|----------|-------------|---------|
| `scenario_name` | Name from the scenario file | `Submit Order AAA` |
| `run_name` | Normalized name with timestamp | `submit_order_aaa_20260404_093303` |
| `run_datetime` | Run start time (UTC, ISO 8601) | `2026-04-04T09:33:03Z` |
| `run_id` | Unique UUID for this run | `a1b2c3d4-...` |

Variables defined in `set` steps are also available in subsequent steps.

### Template Helper Functions

| Function | Description | Example | Output |
|----------|-------------|---------|--------|
| `uuid()` | Generate a UUID v4 | `{{ uuid() }}` | `f04acb56-afec-...` |
| `now()` | Current datetime (ISO 8601) | `{{ now() }}` | `2026-04-04T09:33:03.854024` |
| `today()` | Current date (ISO 8601) | `{{ today() }}` | `2026-04-04` |
| `epoch()` | Unix timestamp (seconds) | `{{ epoch() }}` | `1775364783` |
| `epoch_ms()` | Unix timestamp (milliseconds) | `{{ epoch_ms() }}` | `1775364783854` |
| `date_add(base, weeks, days, hours, minutes, seconds)` | Add offset to a datetime | `{{ date_add(now(), days=1) }}` | `2026-04-05T09:33:03.854024` |
| `dt_format(value, fmt)` | Format a datetime | `{{ dt_format(now(), '%Y-%m-%d') }}` | `2026-04-04` |
| `seq(name)` | Auto-incrementing counter | `{{ seq() }}` | `1`, `2`, `3`, ... |
| `random_string(length)` | Random alphanumeric string | `{{ random_string(16) }}` | `aB3kZ9mQ4xR7wL2p` |
| `randint(a, b)` | Random integer in range [a, b] | `{{ randint(1, 100) }}` | `42` |
| `choice(seq)` | Random element from a sequence | `{{ choice(['a','b','c']) }}` | `b` |
| `b64encode(value)` | Base64 encode | `{{ b64encode('hello') }}` | `aGVsbG8=` |
| `b64decode(value)` | Base64 decode | `{{ b64decode('aGVsbG8=') }}` | `hello` |
| `md5(value)` | MD5 hash | `{{ md5('hello') }}` | `5d41402abc4b2a76...` |
| `sha256(value)` | SHA-256 hash | `{{ sha256('hello') }}` | `2cf24dba5fb0a30e...` |
| `urlencode(value)` | URL encode | `{{ urlencode('a b') }}` | `a%20b` |
| `urldecode(value)` | URL decode | `{{ urldecode('a%20b') }}` | `a b` |

#### `date_add` Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `base` | string or datetime | **Required** | Base datetime (ISO 8601 string or datetime object) |
| `weeks` | int | `0` | Number of weeks to add |
| `days` | int | `0` | Number of days to add |
| `hours` | int | `0` | Number of hours to add |
| `minutes` | int | `0` | Number of minutes to add |
| `seconds` | int | `0` | Number of seconds to add |

#### `seq` Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | `default` | Counter name. Each name maintains its own independent counter starting at 0. |

---

## Complete Example

```yaml
name: Submit Order

kafka:
  default:
    bootstrap_servers: "kafka-broker:9092"

defaults:
  headers:
    content-type: application/json

steps:
  - set:
      user_id: "{{ uuid() }}"
      order_id: "{{ uuid() }}"
      order_date: "{{ now() }}"

  - send:
      topic: "orders"
      key: "{{ user_id }}"
      body: "order-created.json"
      headers:
        x-correlation-id: "{{ uuid() }}"
        x-seq: "{{ seq() }}"

  - sleep:
      message: "Waiting {{ order_id }} 500ms"
      duration: 500ms

  - send:
      topic: "orders"
      key: "{{ user_id }}"
      body: "order-confirmed.json"

  - pause:
      message: "Waiting for processing"
      timeout: 5s
```
