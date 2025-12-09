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

