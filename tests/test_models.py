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

