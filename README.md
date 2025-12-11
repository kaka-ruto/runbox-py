# Runbox Python Client

Official Python client for [Runbox](https://github.com/anywaye/runbox) - a fast, secure API for running code in isolated containers.

[![PyPI version](https://badge.fury.io/py/runbox-client.svg)](https://badge.fury.io/py/runbox-client)
[![CI](https://github.com/anywaye/runbox-py/actions/workflows/ci.yml/badge.svg)](https://github.com/anywaye/runbox-py/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install runbox-client
```

## Quick Start

```python
from runbox_client import Client

# Create a client
client = Client(
    url="http://localhost:8080",
    api_key="your-api-key"
)

# Step 1: Set up a container and get environment info
setup = client.setup(
    identifier="my-session",
    language="python"
)

print(setup.container_id)  # => "runbox-my-session-python"
print(setup.environment_snapshot.runtime_version)  # => "3.11.6"
print(setup.environment_snapshot.packages["requests"])  # => "2.31.0"

# Step 2: Run code in the container
result = client.run(
    container_id=setup.container_id,
    files=[{"path": "main.py", "content": "print('Hello!')"}],
    run_command="python main.py"
)

print(result.stdout)  # => "Hello!\n"
print(result.success)  # => True
```

## Configuration

### Using Environment Variables

```bash
export RUNBOX_URL=http://localhost:8080
export RUNBOX_API_KEY=your-api-key
```

```python
from runbox_client import Client

# Will use environment variables
client = Client()
```

### Explicit Configuration

```python
client = Client(
    url="http://localhost:8080",
    api_key="your-api-key",
    timeout=120  # HTTP timeout in seconds
)
```

## Usage

### Setting Up a Container

```python
setup = client.setup(
    identifier="session-123",
    language="python",
    env={"API_KEY": "secret"},      # Optional: environment variables
    memory="512m",                   # Optional: memory limit
    network_allow=["api.stripe.com"] # Optional: allowed network destinations
)

# Access environment information
print(setup.container_id)  # => "runbox-session-123-python"
print(setup.cached)        # => False (True if container was reused)

env = setup.environment_snapshot
print(env.os_name)          # => "debian"
print(env.os_version)       # => "12"
print(env.runtime_name)     # => "python"
print(env.runtime_version)  # => "3.11.6"
print(env.packages)         # => {"pip": "23.0.1", "requests": "2.31.0", ...}
```

### Running Code

```python
result = client.run(
    container_id="runbox-session-123-python",
    files=[{"path": "main.py", "content": "print('Hello!')"}],
    run_command="python main.py",
    env={"DEBUG": "true"},  # Optional: runtime environment variables
    timeout=30              # Optional: execution timeout in seconds
)

print(result.success)          # => True
print(result.exit_code)        # => 0
print(result.stdout)           # => "Hello!\n"
print(result.stderr)           # => ""
print(result.execution_time_ms) # => 42
print(result.timed_out)        # => False
```

### Installing Dependencies On-The-Fly

Install new dependencies before running code:

```python
# Python example
result = client.run(
    container_id=container_id,
    files=[{"path": "main.py", "content": "import requests; print(requests.__version__)"}],
    run_command="python main.py",
    new_dependencies=["requests==2.31.0", "pytest"]
)

print(result.packages)  # => {"pip": "23.0.1", "requests": "2.31.0", "pytest": "7.4.0", ...}

# Ruby example
result = client.run(
    container_id=container_id,
    files=[{"path": "main.rb", "content": "require 'rake'; puts Rake::VERSION"}],
    run_command="ruby main.rb",
    new_dependencies=["rake", "rspec"]
)

# Shell example (uses apk)
result = client.run(
    container_id=container_id,
    files=[{"path": "script.sh", "content": "#!/bin/sh\ncurl --version"}],
    run_command="sh script.sh",
    new_dependencies=["curl", "jq", "git"]
)
```

**Note:** The `packages` field is only included in the result when `new_dependencies` are provided.

### Async Support

```python
import asyncio
from runbox_client import AsyncClient

async def main():
    async with AsyncClient(url="http://localhost:8080", api_key="your-api-key") as client:
        # Setup container
        setup = await client.setup(
            identifier="session-123",
            language="python"
        )
        
        # Run code
        result = await client.run(
            container_id=setup.container_id,
            files=[{"path": "main.py", "content": "print('Hello!')"}],
            run_command="python main.py"
        )
        
        print(result.stdout)

asyncio.run(main())
```

### Cleanup Containers

```python
deleted = client.delete_containers("session-123")
print(deleted)  # => ["runbox-session-123-python"]
```

### Check Health

```python
health = client.health()
print(health.status)  # => "healthy"
print(health.version) # => "1.0.0"
```

## API Reference

### `client.setup(identifier, language, **options)`

Set up a container and get environment information.

**Parameters:**
- `identifier` (str, required): Unique identifier for container reuse
- `language` (str, required): Programming language (`"python"`, `"ruby"`, `"shell"`)
- `env` (dict, optional): Environment variables to set
- `timeout` (int, optional): Default timeout in seconds
- `memory` (str, optional): Memory limit (e.g., `"256m"`, `"1g"`)
- `network_allow` (list[str], optional): Allowed network destinations

**Returns:** `SetupResult` with:
- `container_id`: Container ID to use in `run()` calls
- `cached`: Whether container was reused
- `environment_snapshot`: Environment information (OS, runtime, packages)

### `client.run(container_id, files, run_command, **options)`

Run code in a container that was set up via `setup()`.

**Parameters:**
- `container_id` (str, required): Container ID from `setup()` response
- `files` (list[dict], required): Files to write before running
- `run_command` (str, required): Command to run
- `env` (dict, optional): Runtime environment variables
- `timeout` (int, optional): Execution timeout in seconds

**Returns:** `RunResult` with:
- `success`: Whether run succeeded (exit code 0)
- `exit_code`: Process exit code
- `stdout`: Standard output
- `stderr`: Standard error
- `execution_time_ms`: Execution time in milliseconds
- `timed_out`: Whether run timed out

## Error Handling

```python
from runbox_client import (
    Client,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    RunError,
    ConnectionError,
)

try:
    setup = client.setup(identifier="test", language="python")
    result = client.run(
        container_id=setup.container_id,
        files=[{"path": "main.py", "content": "print('hi')"}],
        run_command="python main.py"
    )
except AuthenticationError:
    print("Invalid API key")
except NotFoundError:
    print("Container not found (did you call setup first?)")
except ValidationError as e:
    print(f"Invalid request: {e}")
except RunError as e:
    print(f"Run failed: {e}")
except ConnectionError as e:
    print(f"Could not connect: {e}")
```

## Development

### Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Running Integration Tests

Integration tests require a running Runbox server:

```bash
# Start Runbox server (in another terminal)
cd ../runbox
docker-compose up

# Run integration tests
export RUNBOX_URL=http://localhost:8080
export RUNBOX_API_KEY=your-api-key
python examples/integration_test.py
```

### Linting & Typing

```bash
ruff check .
mypy src
```

### CI/CD

- **CI**: Runs on every push and PR
  - Tests on Python 3.9, 3.10, 3.11, 3.12
  - Linting with Ruff
  - Type checking with MyPy
  - Integration tests against live Runbox server

- **CD**: Publishes to PyPI on version tags
  - Create a tag: `git tag v1.0.0 && git push --tags`
  - Uses [Trusted Publishing](https://docs.pypi.org/trusted-publishers/)

## License

MIT License - see [LICENSE](LICENSE) for details.
