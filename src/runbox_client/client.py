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

