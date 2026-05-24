"""Data classes for history inputs and persisted history records."""

from dataclasses import dataclass, field


@dataclass
class HookHistoryEntry:
    """Structured record for a single hook lifecycle event.

    Attributes:
        hook_event: Hook lifecycle event name.
        script: Hook script name.
        status: High-level outcome such as success, skipped, or blocked.
        exit_code: Process exit code reported by the hook.
        target_files: Optional list of files handled by the hook.
        message: Optional short detail about the outcome.
        tool_name: Optional originating tool name from the hook payload.

    """

    hook_event: str
    script: str
    status: str
    exit_code: int
    target_files: list[str] | None = field(default=None)
    message: str | None = field(default=None)
    tool_name: str | None = field(default=None)


@dataclass
class MessageHistoryEntry:
    """Structured record for a single message history event.

    Attributes:
        event: Hook event name associated with the message record.
        session_id: Session identifier from hook payload.
        message: Latest transcript message payload, if present.

    """

    event: str
    session_id: str
    message: str | None = field(default=None)


@dataclass
class HookHistoryRecord:
    """Persisted hook history record ready for JSON serialization.

    Attributes:
        timestamp: ISO8601 timestamp in JST.
        hook_event: Hook lifecycle event name.
        script: Hook script name.
        status: High-level outcome such as success, skipped, or blocked.
        exit_code: Process exit code reported by the hook.
        target_files: Optional list of files handled by the hook.
        message: Optional short detail about the outcome.
        tool_name: Optional originating tool name from the hook payload.

    """

    timestamp: str
    hook_event: str
    script: str
    status: str
    exit_code: int
    target_files: list[str] | None = field(default=None)
    message: str | None = field(default=None)
    tool_name: str | None = field(default=None)

    def to_dict(self) -> dict[str, object]:
        """Convert the record to a compact dictionary for JSONL output."""
        record: dict[str, object] = {
            "timestamp": self.timestamp,
            "hook_event": self.hook_event,
            "script": self.script,
            "status": self.status,
            "exit_code": self.exit_code,
        }
        if self.target_files:
            record["target_files"] = self.target_files
        if self.message:
            record["message"] = self.message
        if self.tool_name:
            record["tool_name"] = self.tool_name
        return record


@dataclass
class MessageHistoryRecord:
    """Persisted message history record ready for JSON serialization.

    Attributes:
        timestamp: ISO8601 timestamp in JST.
        event: Hook event name associated with the message record.
        session_id: Session identifier from hook payload.
        message: Latest transcript message payload, if present.

    """

    timestamp: str
    event: str
    session_id: str
    message: str | None = field(default=None)

    def to_dict(self) -> dict[str, object]:
        """Convert the record to a dictionary for JSONL output."""
        return {
            "timestamp": self.timestamp,
            "event": self.event,
            "session_id": self.session_id,
            "message": self.message,
        }
