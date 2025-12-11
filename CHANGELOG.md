# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2025-12-11

### Breaking Changes

- **Renamed `entrypoint` to `run_command`** in `run()` methods.
  - The `entrypoint` parameter (file path) is removed.
  - New `run_command` parameter accepts a full shell command string.
  - Example: `run_command="python main.py"` instead of `entrypoint="main.py"`.

### Added

- **`run_command` support**: Execute arbitrary shell commands (e.g. `pytest tests/`, `bundle exec rails test`).

### Migration Guide

**Before:**
```python
client.run(
    entrypoint="main.py",
    # ...
)
```

**After:**
```python
client.run(
    run_command="python main.py",
    # ...
)
```

## [1.1.0] - 2025-12-10

### Added

- **`new_dependencies` parameter** in `run()` method: Install dependencies on-the-fly before code execution
  - Python: `["requests==2.31.0", "pytest"]`
  - Ruby: `["rake", "rspec"]`
  - Shell: `["curl", "jq", "git"]` (uses apk)
- **`packages` field** in `RunResult`: Returns updated package list when dependencies are installed
  - Only included when `new_dependencies` were provided
  - Dictionary of package names to versions

### Example

```python
# Install dependencies and run code
result = client.run(
    container_id=container_id,
    files=[{"path": "main.py", "content": "import requests; print(requests.__version__)"}],
    entrypoint="main.py",
    new_dependencies=["requests==2.31.0"]
)

print(result.packages)  # {"pip": "23.0.1", "requests": "2.31.0", ...}
```

## [1.0.0] - 2025-12-10

### Breaking Changes

- **New API workflow**: The client now uses a two-step `setup()` + `run()` workflow instead of a single `run()` call
- `run()` method signature changed:
  - Now requires `container_id` (from `setup()` response) instead of `identifier` and `language`
  - Removed `memory` and `network_allow` parameters (these are now in `setup()`)
- `RunResult` model no longer includes `container_id` and `cached` fields (these are now in `SetupResult`)

### Added

- **`setup()` method**: Creates or reuses a container and returns environment information
  - Returns `SetupResult` with `container_id`, `cached`, and `environment_snapshot`
  - `environment_snapshot` includes OS name/version, runtime name/version, and installed packages
- **`SetupResult` class**: New result object for `setup()` responses
- **`EnvironmentSnapshot` class**: Contains detailed environment information
  - `os_name`, `os_version`: Operating system details
  - `runtime_name`, `runtime_version`: Runtime details (e.g., Python 3.11.6)
  - `packages`: Dictionary of installed package names and versions
- **`NotFoundError`**: New exception class for 404 responses (e.g., container not found)

### Changed

- Renamed `ExecutionError` to `RunError` to match new terminology
- Updated error handling to include 404 Not Found responses
- `run()` method is now focused solely on code execution in pre-setup containers

### Migration Guide

**Before (v0.1.0):**
```python
result = client.run(
    identifier="session-123",
    language="python",
    files=[{"path": "main.py", "content": "print('hi')"}],
    entrypoint="main.py"
)

print(result.container_id)  # "runbox-session-123-python"
print(result.cached)        # True/False
```

**After (v1.0.0):**
```python
# Step 1: Setup container
setup = client.setup(
    identifier="session-123",
    language="python"
)

print(setup.container_id)  # "runbox-session-123-python"
print(setup.cached)        # True/False
print(setup.environment_snapshot.runtime_version)  # "3.11.6"

# Step 2: Run code
result = client.run(
    container_id=setup.container_id,
    files=[{"path": "main.py", "content": "print('hi')"}],
    entrypoint="main.py"
)

# Note: result no longer has container_id or cached fields
```

## [0.1.0] - 2024-12-01

### Added

- Initial release
- `run()` method for executing code in isolated containers
- Support for Python, Ruby, and Shell languages
- Container reuse via identifiers
- Environment variables, timeouts, memory limits, network allowlisting
- `delete_containers()` method for cleanup
- `health()` method for health checks
- Comprehensive error handling
- Configuration via environment variables or constructor parameters
- Both synchronous (`Client`) and asynchronous (`AsyncClient`) implementations
