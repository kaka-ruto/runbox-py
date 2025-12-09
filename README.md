## README.md

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

# Run some code
result = client.run(
    identifier="my-session",
    language="python",
    files=[{"path": "main.py", "content": "print('Hello!')"}],
    entrypoint="main.py"
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
    timeout=120  # HTTP timeout
)
```

## Usage

### Basic Execution

```python
result = client.run(
    identifier="session-123",
    language="python",
    files=[{"path": "main.py", "content": "print('Hello!')"}],
    entrypoint="main.py"
)
```

### With Environment Variables

```python
result = client.run(
    identifier="session-123",
    language="python",
    files=[{"path": "main.py", "content": "import os; print(os.environ['API_KEY'])"}],
    entrypoint="main.py",
    env={"API_KEY": "secret"}
)
```

### With Network Access

```python
result = client.run(
    identifier="session-123",
    language="python",
    files=[{"path": "main.py", "content": "..."}],
    entrypoint="main.py",
    network_allow=["api.stripe.com"]
)
```

### Async Support

```python
import asyncio
from runbox_client import AsyncClient

async def main():
    client = AsyncClient(
        url="http://localhost:8080",
        api_key="your-api-key"
    )

    result = await client.run(
        identifier="session-123",
        language="python",
        files=[{"path": "main.py", "content": "print('Hello!')"}],
        entrypoint="main.py"
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
```

## Result Object

```python
result.success          # => True/False
result.exit_code        # => 0
result.stdout           # => "output"
result.stderr           # => "errors"
result.execution_time_ms  # => 123
result.container_id     # => "runbox-session-123-python"
result.cached           # => True/False
result.timeout_exceeded # => True/False
```

## Error Handling

```python
from runbox_client import (
    Client,
    AuthenticationError,
    ValidationError,
    ExecutionError,
    ConnectionError,
)

try:
    result = client.run(...)
except AuthenticationError:
    print("Invalid API key")
except ValidationError as e:
    print(f"Invalid request: {e}")
except ExecutionError as e:
    print(f"Execution failed: {e}")
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
  - Create a tag: `git tag v0.1.0 && git push --tags`
  - Uses [Trusted Publishing](https://docs.pypi.org/trusted-publishers/)

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## pyproject.toml

```toml
[project]
name = "runbox-client"
version = "0.1.0"
description = "Official Python client for Runbox - secure code execution API"
readme = "README.md"
license = { text = "MIT" }
requires-python = ">=3.9"
authors = [
    { name = "Anywaye", email = "hello@anywaye.com" }
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
dependencies = [
    "httpx>=0.26.0",
    "pydantic>=2.5.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-httpx>=0.28.0",
    "ruff>=0.1.0",
    "mypy>=1.8.0",
]

[project.urls]
Homepage = "https://github.com/anywaye/runbox-py"
Documentation = "https://github.com/anywaye/runbox-py#readme"
Repository = "https://github.com/anywaye/runbox-py"
Changelog = "https://github.com/anywaye/runbox-py/blob/main/CHANGELOG.md"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/runbox_client"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.ruff]
line-length = 100
target-version = "py39"

[tool.mypy]
python_version = "3.9"
strict = true
```

---

## src/runbox_client/**init**.py

```python
"""Runbox Python Client - Official client for Runbox API."""

from runbox_client.client import Client, AsyncClient
from runbox_client.models import RunResult, HealthResult, FileInput
from runbox_client.exceptions import (
    RunboxError,
    ConfigurationError,
    ConnectionError,
    AuthenticationError,
    ValidationError,
    ExecutionError,
)

__version__ = "0.1.0"

__all__ = [
    "Client",
    "AsyncClient",
    "RunResult",
    "HealthResult",
    "FileInput",
    "RunboxError",
    "ConfigurationError",
    "ConnectionError",
    "AuthenticationError",
    "ValidationError",
    "ExecutionError",
]
```

---

## src/runbox_client/exceptions.py

```python
"""Exceptions for Runbox client."""


class RunboxError(Exception):
    """Base exception for Runbox client."""
    pass


class ConfigurationError(RunboxError):
    """Configuration error."""
    pass


class ConnectionError(RunboxError):
    """Connection error."""
    pass


class AuthenticationError(RunboxError):
    """Authentication error (401)."""
    pass


class ValidationError(RunboxError):
    """Validation error (400)."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.details = details


class ExecutionError(RunboxError):
    """Execution error (500)."""
    pass
```

---

## src/runbox_client/models.py

```python
"""Data models for Runbox client."""

from pydantic import BaseModel


class FileInput(BaseModel):
    """A file to be written to the container."""

    path: str
    content: str


class RunResult(BaseModel):
    """Result of code execution."""

    success: bool
    exit_code: int
    stdout: str
    stderr: str
    execution_time_ms: int
    container_id: str
    cached: bool
    timeout_exceeded: bool = False

    @property
    def failed(self) -> bool:
        """Check if execution failed."""
        return not self.success

    @property
    def timed_out(self) -> bool:
        """Check if execution timed out."""
        return self.timeout_exceeded


class HealthResult(BaseModel):
    """Result of health check."""

    status: str
    version: str


class DeleteResult(BaseModel):
    """Result of container deletion."""

    deleted: list[str]
```

---

## src/runbox_client/client.py

```python
"""Runbox client implementations."""

import os
from typing import Any

import httpx

from runbox_client.exceptions import (
    ConfigurationError,
    ConnectionError,
    AuthenticationError,
    ValidationError,
    ExecutionError,
)
from runbox_client.models import RunResult, HealthResult, DeleteResult, FileInput


class Client:
    """Synchronous Runbox client."""

    def __init__(
        self,
        url: str | None = None,
        api_key: str | None = None,
        timeout: float = 120.0,
    ):
        """
        Initialize the client.

        Args:
            url: Runbox server URL (default: RUNBOX_URL env var or http://localhost:8080)
            api_key: API key (default: RUNBOX_API_KEY env var)
            timeout: HTTP timeout in seconds
        """
        self.url = url or os.environ.get("RUNBOX_URL", "http://localhost:8080")
        self.api_key = api_key or os.environ.get("RUNBOX_API_KEY")
        self.timeout = timeout

        self._validate_config()

        self._client = httpx.Client(
            base_url=self.url,
            timeout=timeout,
            headers={"Authorization": f"Bearer {self.api_key}"},
        )

    def _validate_config(self) -> None:
        """Validate configuration."""
        if not self.url:
            raise ConfigurationError("URL is required")
        if not self.api_key:
            raise ConfigurationError("API key is required")

    def run(
        self,
        identifier: str,
        language: str,
        files: list[dict[str, str] | FileInput],
        entrypoint: str,
        env: dict[str, str] | None = None,
        timeout: int | None = None,
        memory: str | None = None,
        network_allow: list[str] | None = None,
    ) -> RunResult:
        """
        Execute code in a sandboxed container.

        Args:
            identifier: Unique identifier for container reuse
            language: Programming language (python, ruby, shell)
            files: List of files to write
            entrypoint: File to execute
            env: Environment variables
            timeout: Execution timeout in seconds
            memory: Memory limit (e.g., "256m")
            network_allow: Allowed network destinations

        Returns:
            RunResult with execution output
        """
        # Normalize files
        normalized_files = []
        for f in files:
            if isinstance(f, FileInput):
                normalized_files.append({"path": f.path, "content": f.content})
            else:
                normalized_files.append(f)

        payload: dict[str, Any] = {
            "identifier": identifier,
            "language": language,
            "files": normalized_files,
            "entrypoint": entrypoint,
        }

        if env:
            payload["env"] = env
        if timeout is not None:
            payload["timeout"] = timeout
        if memory is not None:
            payload["memory"] = memory
        if network_allow is not None:
            payload["network_allow"] = network_allow

        response = self._post("/v1/run", payload)
        return RunResult(**response)

    def delete_containers(self, identifier: str) -> list[str]:
        """
        Delete all containers for an identifier.

        Args:
            identifier: Container identifier

        Returns:
            List of deleted container IDs
        """
        response = self._delete(f"/v1/containers/{identifier}")
        result = DeleteResult(**response)
        return result.deleted

    def health(self) -> HealthResult:
        """
        Check service health.

        Returns:
            HealthResult with status and version
        """
        response = self._get("/v1/health", auth=False)
        return HealthResult(**response)

    def _get(self, path: str, auth: bool = True) -> dict[str, Any]:
        """Make GET request."""
        try:
            headers = {}
            if not auth:
                headers = {"Authorization": ""}
            response = self._client.get(path, headers=headers if not auth else None)
            return self._handle_response(response)
        except httpx.ConnectError as e:
            raise ConnectionError(f"Failed to connect to Runbox: {e}")
        except httpx.TimeoutException as e:
            raise ConnectionError(f"Request timed out: {e}")

    def _post(self, path: str, data: dict[str, Any]) -> dict[str, Any]:
        """Make POST request."""
        try:
            response = self._client.post(path, json=data)
            return self._handle_response(response)
        except httpx.ConnectError as e:
            raise ConnectionError(f"Failed to connect to Runbox: {e}")
        except httpx.TimeoutException as e:
            raise ConnectionError(f"Request timed out: {e}")

    def _delete(self, path: str) -> dict[str, Any]:
        """Make DELETE request."""
        try:
            response = self._client.delete(path)
            return self._handle_response(response)
        except httpx.ConnectError as e:
            raise ConnectionError(f"Failed to connect to Runbox: {e}")
        except httpx.TimeoutException as e:
            raise ConnectionError(f"Request timed out: {e}")

    def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        """Handle HTTP response."""
        if response.status_code == 401:
            raise AuthenticationError("Invalid API key")

        if response.status_code == 400:
            data = response.json()
            raise ValidationError(data.get("detail", "Validation error"), details=data)

        if response.status_code == 422:
            data = response.json()
            raise ValidationError(data.get("detail", "Validation error"), details=data)

        if response.status_code >= 500:
            data = response.json() if response.content else {}
            raise ExecutionError(data.get("detail", "Execution failed"))

        return response.json()

    def close(self) -> None:
        """Close the client."""
        self._client.close()

    def __enter__(self) -> "Client":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()


class AsyncClient:
    """Asynchronous Runbox client."""

    def __init__(
        self,
        url: str | None = None,
        api_key: str | None = None,
        timeout: float = 120.0,
    ):
        """
        Initialize the async client.

        Args:
            url: Runbox server URL
            api_key: API key
            timeout: HTTP timeout in seconds
        """
        self.url = url or os.environ.get("RUNBOX_URL", "http://localhost:8080")
        self.api_key = api_key or os.environ.get("RUNBOX_API_KEY")
        self.timeout = timeout

        self._validate_config()

        self._client = httpx.AsyncClient(
            base_url=self.url,
            timeout=timeout,
            headers={"Authorization": f"Bearer {self.api_key}"},
        )

    def _validate_config(self) -> None:
        """Validate configuration."""
        if not self.url:
            raise ConfigurationError("URL is required")
        if not self.api_key:
            raise ConfigurationError("API key is required")

    async def run(
        self,
        identifier: str,
        language: str,
        files: list[dict[str, str] | FileInput],
        entrypoint: str,
        env: dict[str, str] | None = None,
        timeout: int | None = None,
        memory: str | None = None,
        network_allow: list[str] | None = None,
    ) -> RunResult:
        """Execute code in a sandboxed container."""
        normalized_files = []
        for f in files:
            if isinstance(f, FileInput):
                normalized_files.append({"path": f.path, "content": f.content})
            else:
                normalized_files.append(f)

        payload: dict[str, Any] = {
            "identifier": identifier,
            "language": language,
            "files": normalized_files,
            "entrypoint": entrypoint,
        }

        if env:
            payload["env"] = env
        if timeout is not None:
            payload["timeout"] = timeout
        if memory is not None:
            payload["memory"] = memory
        if network_allow is not None:
            payload["network_allow"] = network_allow

        response = await self._post("/v1/run", payload)
        return RunResult(**response)

    async def delete_containers(self, identifier: str) -> list[str]:
        """Delete all containers for an identifier."""
        response = await self._delete(f"/v1/containers/{identifier}")
        result = DeleteResult(**response)
        return result.deleted

    async def health(self) -> HealthResult:
        """Check service health."""
        response = await self._get("/v1/health", auth=False)
        return HealthResult(**response)

    async def _get(self, path: str, auth: bool = True) -> dict[str, Any]:
        """Make GET request."""
        try:
            response = await self._client.get(path)
            return self._handle_response(response)
        except httpx.ConnectError as e:
            raise ConnectionError(f"Failed to connect to Runbox: {e}")
        except httpx.TimeoutException as e:
            raise ConnectionError(f"Request timed out: {e}")

    async def _post(self, path: str, data: dict[str, Any]) -> dict[str, Any]:
        """Make POST request."""
        try:
            response = await self._client.post(path, json=data)
            return self._handle_response(response)
        except httpx.ConnectError as e:
            raise ConnectionError(f"Failed to connect to Runbox: {e}")
        except httpx.TimeoutException as e:
            raise ConnectionError(f"Request timed out: {e}")

    async def _delete(self, path: str) -> dict[str, Any]:
        """Make DELETE request."""
        try:
            response = await self._client.delete(path)
            return self._handle_response(response)
        except httpx.ConnectError as e:
            raise ConnectionError(f"Failed to connect to Runbox: {e}")
        except httpx.TimeoutException as e:
            raise ConnectionError(f"Request timed out: {e}")

    def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        """Handle HTTP response."""
        if response.status_code == 401:
            raise AuthenticationError("Invalid API key")

        if response.status_code == 400:
            data = response.json()
            raise ValidationError(data.get("detail", "Validation error"), details=data)

        if response.status_code == 422:
            data = response.json()
            raise ValidationError(data.get("detail", "Validation error"), details=data)

        if response.status_code >= 500:
            data = response.json() if response.content else {}
            raise ExecutionError(data.get("detail", "Execution failed"))

        return response.json()

    async def close(self) -> None:
        """Close the client."""
        await self._client.aclose()

    async def __aenter__(self) -> "AsyncClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
```

---

## tests/conftest.py

```python
"""Pytest configuration for Runbox client tests."""

import os
import pytest

# Set test environment variables
os.environ["RUNBOX_URL"] = "http://localhost:8080"
os.environ["RUNBOX_API_KEY"] = "test-api-key"


@pytest.fixture
def api_key() -> str:
    """Return test API key."""
    return "test-api-key"


@pytest.fixture
def base_url() -> str:
    """Return test base URL."""
    return "http://localhost:8080"
```

---

## tests/test_client.py

```python
"""Tests for Runbox client."""

import pytest
from pytest_httpx import HTTPXMock

from runbox_client import (
    Client,
    AsyncClient,
    AuthenticationError,
    ValidationError,
    ConfigurationError,
)


class TestClient:
    """Tests for synchronous client."""

    def test_run_executes_code_successfully(self, httpx_mock: HTTPXMock):
        """Client executes code and returns result."""
        httpx_mock.add_response(
            method="POST",
            url="http://localhost:8080/v1/run",
            json={
                "success": True,
                "exit_code": 0,
                "stdout": "Hello!\n",
                "stderr": "",
                "execution_time_ms": 123,
                "container_id": "runbox-test-python",
                "cached": False,
                "timeout_exceeded": False,
            },
        )

        client = Client(url="http://localhost:8080", api_key="test-key")
        result = client.run(
            identifier="test-123",
            language="python",
            files=[{"path": "main.py", "content": "print('Hello!')"}],
            entrypoint="main.py",
        )

        assert result.success is True
        assert result.stdout == "Hello!\n"
        assert result.exit_code == 0

    def test_run_handles_failure(self, httpx_mock: HTTPXMock):
        """Client handles execution failure."""
        httpx_mock.add_response(
            method="POST",
            url="http://localhost:8080/v1/run",
            json={
                "success": False,
                "exit_code": 1,
                "stdout": "",
                "stderr": "Error",
                "execution_time_ms": 50,
                "container_id": "runbox-test-python",
                "cached": False,
                "timeout_exceeded": False,
            },
        )

        client = Client(url="http://localhost:8080", api_key="test-key")
        result = client.run(
            identifier="test",
            language="python",
            files=[{"path": "main.py", "content": "exit(1)"}],
            entrypoint="main.py",
        )

        assert result.success is False
        assert result.failed is True
        assert result.exit_code == 1

    def test_run_raises_on_auth_error(self, httpx_mock: HTTPXMock):
        """Client raises AuthenticationError on 401."""
        httpx_mock.add_response(
            method="POST",
            url="http://localhost:8080/v1/run",
            status_code=401,
            json={"detail": "Invalid API key"},
        )

        client = Client(url="http://localhost:8080", api_key="wrong-key")

        with pytest.raises(AuthenticationError):
            client.run(
                identifier="test",
                language="python",
                files=[{"path": "main.py", "content": "print('hi')"}],
                entrypoint="main.py",
            )

    def test_run_raises_on_validation_error(self, httpx_mock: HTTPXMock):
        """Client raises ValidationError on 400."""
        httpx_mock.add_response(
            method="POST",
            url="http://localhost:8080/v1/run",
            status_code=400,
            json={"detail": "Unsupported language"},
        )

        client = Client(url="http://localhost:8080", api_key="test-key")

        with pytest.raises(ValidationError) as exc_info:
            client.run(
                identifier="test",
                language="cobol",
                files=[{"path": "main.cob", "content": "..."}],
                entrypoint="main.cob",
            )

        assert "Unsupported language" in str(exc_info.value)

    def test_delete_containers(self, httpx_mock: HTTPXMock):
        """Client deletes containers."""
        httpx_mock.add_response(
            method="DELETE",
            url="http://localhost:8080/v1/containers/test-123",
            json={"deleted": ["runbox-test-123-python"]},
        )

        client = Client(url="http://localhost:8080", api_key="test-key")
        deleted = client.delete_containers("test-123")

        assert deleted == ["runbox-test-123-python"]

    def test_health_check(self, httpx_mock: HTTPXMock):
        """Client checks health."""
        httpx_mock.add_response(
            method="GET",
            url="http://localhost:8080/v1/health",
            json={"status": "healthy", "version": "0.1.0"},
        )

        client = Client(url="http://localhost:8080", api_key="test-key")
        health = client.health()

        assert health.status == "healthy"
        assert health.version == "0.1.0"

    def test_requires_api_key(self):
        """Client requires API key."""
        # Clear environment variable
        import os
        original = os.environ.get("RUNBOX_API_KEY")
        os.environ["RUNBOX_API_KEY"] = ""

        try:
            with pytest.raises(ConfigurationError):
                Client(url="http://localhost:8080", api_key=None)
        finally:
            if original:
                os.environ["RUNBOX_API_KEY"] = original

    def test_context_manager(self, httpx_mock: HTTPXMock):
        """Client works as context manager."""
        httpx_mock.add_response(
            method="GET",
            url="http://localhost:8080/v1/health",
            json={"status": "healthy", "version": "0.1.0"},
        )

        with Client(url="http://localhost:8080", api_key="test-key") as client:
            health = client.health()
            assert health.status == "healthy"


class TestAsyncClient:
    """Tests for async client."""

    @pytest.mark.asyncio
    async def test_run_executes_code_successfully(self, httpx_mock: HTTPXMock):
        """Async client executes code."""
        httpx_mock.add_response(
            method="POST",
            url="http://localhost:8080/v1/run",
            json={
                "success": True,
                "exit_code": 0,
                "stdout": "Hello!\n",
                "stderr": "",
                "execution_time_ms": 123,
                "container_id": "runbox-test-python",
                "cached": False,
                "timeout_exceeded": False,
            },
        )

        async with AsyncClient(url="http://localhost:8080", api_key="test-key") as client:
            result = await client.run(
                identifier="test",
                language="python",
                files=[{"path": "main.py", "content": "print('Hello!')"}],
                entrypoint="main.py",
            )

        assert result.success is True
        assert result.stdout == "Hello!\n"
```

---

## tests/test_models.py

```python
"""Tests for Runbox client models."""

import pytest

from runbox_client.models import RunResult, HealthResult, FileInput


class TestRunResult:
    """Tests for RunResult model."""

    def test_success_result(self):
        """RunResult correctly identifies success."""
        result = RunResult(
            success=True,
            exit_code=0,
            stdout="Hello\n",
            stderr="",
            execution_time_ms=100,
            container_id="runbox-test-python",
            cached=False,
            timeout_exceeded=False,
        )

        assert result.success is True
        assert result.failed is False
        assert result.exit_code == 0
        assert result.stdout == "Hello\n"

    def test_failed_result(self):
        """RunResult correctly identifies failure."""
        result = RunResult(
            success=False,
            exit_code=1,
            stdout="",
            stderr="Error",
            execution_time_ms=50,
            container_id="runbox-test-python",
            cached=False,
            timeout_exceeded=False,
        )

        assert result.success is False
        assert result.failed is True
        assert result.exit_code == 1

    def test_timeout_result(self):
        """RunResult correctly identifies timeout."""
        result = RunResult(
            success=False,
            exit_code=124,
            stdout="",
            stderr="Timeout",
            execution_time_ms=30000,
            container_id="runbox-test-python",
            cached=False,
            timeout_exceeded=True,
        )

        assert result.timed_out is True
        assert result.timeout_exceeded is True


class TestFileInput:
    """Tests for FileInput model."""

    def test_creates_file_input(self):
        """FileInput can be created."""
        file = FileInput(path="main.py", content="print('hi')")

        assert file.path == "main.py"
        assert file.content == "print('hi')"


class TestHealthResult:
    """Tests for HealthResult model."""

    def test_creates_health_result(self):
        """HealthResult can be created."""
        health = HealthResult(status="healthy", version="0.1.0")

        assert health.status == "healthy"
        assert health.version == "0.1.0"
```

---

## .gitignore (for runbox-py)

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
ENV/
env/
.venv/

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# Testing
.coverage
htmlcov/
.pytest_cache/
.tox/
.nox/

# Type checking
.mypy_cache/

# OS
.DS_Store
Thumbs.db
```

---

# Summary

I've provided the complete implementation for all three repositories:

## 1. anywaye/runbox (Python Server)

- FastAPI server with `/v1/run`, `/v1/containers/{id}`, `/v1/health` endpoints
- Container management with per-identifier persistence
- Network allowlisting via iptables
- Background cleanup worker
- Docker images for Python, Ruby, Shell
- Comprehensive behavioral tests
- Full documentation

## 2. anywaye/runbox-rb (Ruby Client)

- Gem that wraps HTTP calls to Runbox
- `Runbox::Client` with `run`, `delete_containers`, `health` methods
- `Runbox::Result` with convenient accessors
- Error handling with typed exceptions
- Configuration via environment or explicit
- Full test suite with WebMock

## 3. anywaye/runbox-py (Python Client)

- Package with sync `Client` and `AsyncClient`
- Pydantic models for type safety
- Same API as Ruby client
- Error handling with typed exceptions
- Full test suite with pytest-httpx

---

## Next Steps

1. **Create the repositories** on GitHub
2. **Push the code** to each repo
3. **Build and publish Docker images** to Docker Hub (`runbox/python:3.11`, etc.)
4. **Publish gems/packages** to RubyGems and PyPI
5. **Deploy Runbox** with Kamal
6. **Integrate** into Anywaye Rails app

Would you like me to provide the Kamal deployment configuration for Runbox, or help with any other aspect?
