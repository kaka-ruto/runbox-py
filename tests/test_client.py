"""Tests for Runbox client."""

import pytest
from pytest_httpx import HTTPXMock

from runbox_client import (
    Client,
    AsyncClient,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    ConfigurationError,
)


class TestClient:
    """Tests for synchronous client."""
    
    def test_setup_creates_container(self, httpx_mock: HTTPXMock):
        """Client sets up container and returns environment."""
        httpx_mock.add_response(
            method="POST",
            url="http://localhost:8080/v1/setup",
            json={
                "container_id": "runbox-test-123-python",
                "cached": False,
                "environment_snapshot": {
                    "os_name": "debian",
                    "os_version": "12",
                    "runtime_name": "python",
                    "runtime_version": "3.11.6",
                    "packages": {"pip": "23.0.1", "requests": "2.31.0"},
                },
            },
        )
        
        client = Client(url="http://localhost:8080", api_key="test-key")
        result = client.setup(
            identifier="test-123",
            language="python",
        )
        
        assert result.container_id == "runbox-test-123-python"
        assert result.cached is False
        assert result.environment_snapshot.os_name == "debian"
        assert result.environment_snapshot.runtime_version == "3.11.6"
        assert result.environment_snapshot.packages["pip"] == "23.0.1"
    
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
                "timeout_exceeded": False,
            },
        )
        
        client = Client(url="http://localhost:8080", api_key="test-key")
        result = client.run(
            container_id="runbox-test-123-python",
            files=[{"path": "main.py", "content": "print('Hello!')"}],
            entrypoint="main.py",
        )
        
        assert result.success is True
        assert result.stdout == "Hello!\n"
        assert result.exit_code == 0
        assert result.timed_out is False
    
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
                "timeout_exceeded": False,
            },
        )
        
        client = Client(url="http://localhost:8080", api_key="test-key")
        result = client.run(
            container_id="runbox-test-python",
            files=[{"path": "main.py", "content": "exit(1)"}],
            entrypoint="main.py",
        )
        
        assert result.success is False
        assert result.failed is True
        assert result.exit_code == 1
    
    def test_run_raises_on_container_not_found(self, httpx_mock: HTTPXMock):
        """Client raises NotFoundError when container not found."""
        httpx_mock.add_response(
            method="POST",
            url="http://localhost:8080/v1/run",
            status_code=404,
            json={"detail": "Container not found: runbox-nonexistent-python. Did you call /setup first?"},
        )
        
        client = Client(url="http://localhost:8080", api_key="test-key")
        
        with pytest.raises(NotFoundError) as exc_info:
            client.run(
                container_id="runbox-nonexistent-python",
                files=[{"path": "main.py", "content": "print('hi')"}],
                entrypoint="main.py",
            )
        
        assert "not found" in str(exc_info.value).lower()
    
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
                container_id="runbox-test-python",
                files=[{"path": "main.py", "content": "print('hi')"}],
                entrypoint="main.py",
            )
    
    def test_run_raises_on_validation_error(self, httpx_mock: HTTPXMock):
        """Client raises ValidationError on 400."""
        httpx_mock.add_response(
            method="POST",
            url="http://localhost:8080/v1/run",
            status_code=400,
            json={"detail": "Entrypoint 'missing.py' not found in files"},
        )
        
        client = Client(url="http://localhost:8080", api_key="test-key")
        
        with pytest.raises(ValidationError) as exc_info:
            client.run(
                container_id="runbox-test-python",
                files=[{"path": "main.py", "content": "..."}],
                entrypoint="missing.py",
            )
        
        assert "not found" in str(exc_info.value).lower()
    
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
            json={"status": "healthy", "version": "1.0.0"},
        )
        
        client = Client(url="http://localhost:8080", api_key="test-key")
        health = client.health()
        
        assert health.status == "healthy"
        assert health.version == "1.0.0"
    
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
            json={"status": "healthy", "version": "1.0.0"},
        )
        
        with Client(url="http://localhost:8080", api_key="test-key") as client:
            health = client.health()
            assert health.status == "healthy"


class TestAsyncClient:
    """Tests for async client."""
    
    @pytest.mark.asyncio
    async def test_setup_creates_container(self, httpx_mock: HTTPXMock):
        """Async client sets up container."""
        httpx_mock.add_response(
            method="POST",
            url="http://localhost:8080/v1/setup",
            json={
                "container_id": "runbox-test-python",
                "cached": False,
                "environment_snapshot": {
                    "os_name": "debian",
                    "os_version": "12",
                    "runtime_name": "python",
                    "runtime_version": "3.11.6",
                    "packages": {},
                },
            },
        )
        
        async with AsyncClient(url="http://localhost:8080", api_key="test-key") as client:
            result = await client.setup(
                identifier="test",
                language="python",
            )
        
        assert result.container_id == "runbox-test-python"
        assert result.cached is False
    
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
                "timeout_exceeded": False,
            },
        )
        
        async with AsyncClient(url="http://localhost:8080", api_key="test-key") as client:
            result = await client.run(
                container_id="runbox-test-python",
                files=[{"path": "main.py", "content": "print('Hello!')"}],
                entrypoint="main.py",
            )
        
        assert result.success is True
        assert result.stdout == "Hello!\n"
