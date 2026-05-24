"""Markdown formatter hook script with history recording."""

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from recorder import HistoryRecorder, HookHistoryEntry

_history_recorder = HistoryRecorder()


def _find_mdformat() -> list[str] | None:
    """Locate the mdformat executable in the virtual environment or system PATH.

    Returns:
        A list containing the path to the mdformat executable, or None if
        mdformat is not available.

    """
    venv_scripts = Path(".venv/Scripts/mdformat.exe")
    if venv_scripts.exists():
        return [str(venv_scripts)]
    venv_bin = Path(".venv/bin/mdformat")
    if venv_bin.exists():
        return [str(venv_bin)]
    if shutil.which("mdformat"):
        return ["mdformat"]
    return None


def _find_pymarkdown() -> list[str] | None:
    """Locate the pymarkdown executable in the virtual environment or system PATH.

    Returns:
        A list containing the path to the pymarkdown executable, or None if
        pymarkdown is not available.

    """
    venv_scripts = Path(".venv/Scripts/pymarkdown.exe")
    if venv_scripts.exists():
        return [str(venv_scripts)]
    venv_bin = Path(".venv/bin/pymarkdown")
    if venv_bin.exists():
        return [str(venv_bin)]
    if shutil.which("pymarkdown"):
        return ["pymarkdown"]
    return None


def _collect_markdown_paths(tool_input: dict[str, object]) -> list[str]:
    """Extract Markdown file paths targeted by a tool call from its input payload.

    Args:
        tool_input: The ``tool_input`` dict from the Claude Code hook payload.

    Returns:
        A deduplicated list of ``.md`` or ``.mdx`` file paths found in the payload.

    """
    direct_path = tool_input.get("file_path") or tool_input.get("filePath")
    if isinstance(direct_path, str) and direct_path.endswith((".md", ".mdx")):
        return [direct_path]

    patch_input = tool_input.get("input")
    if not isinstance(patch_input, str):
        return []

    matches = re.findall(
        r"^\*\*\* (?:Add|Update) File: (.+)$",
        patch_input,
        flags=re.MULTILINE,
    )
    markdown_paths: list[str] = []
    for match in matches:
        normalized_path = match.strip()
        if normalized_path.endswith((".md", ".mdx")):
            markdown_paths.append(normalized_path)

    return list(dict.fromkeys(markdown_paths))


def _format_markdown_file(file_path: str) -> tuple[int, str]:
    """Run mdformat and pymarkdown fix/scan on a single Markdown file.

    Args:
        file_path: Path to the Markdown file to format.

    Returns:
        A tuple of (exit_code, violations) where exit_code is 0 on success or
        2 if pymarkdown scan reports remaining violations, and violations is the
        pymarkdown stdout output (empty string on success).

    """
    exit_code = 0
    violations = ""

    mdformat = _find_mdformat()
    if mdformat:
        subprocess.run(  # noqa: S603
            [*mdformat, file_path],
            capture_output=True,
            check=False,
        )

    pymarkdown = _find_pymarkdown()
    if not pymarkdown:
        return exit_code, violations

    config = Path(__file__).parent / ".pymarkdown.json"
    config_args = ["--config", str(config)] if config.exists() else []
    subprocess.run(  # noqa: S603
        [*pymarkdown, *config_args, "fix", file_path],
        capture_output=True,
        check=False,
    )
    result = subprocess.run(  # noqa: S603
        [*pymarkdown, *config_args, "scan", file_path],
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0 and result.stdout.strip():
        violations = result.stdout.strip()
        print(violations)
        exit_code = 2

    return exit_code, violations


def main() -> int:
    """Read hook payload from stdin, format Markdown files, and record history."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    tool_input = data.get("tool_input", {})
    hook_event = str(data.get("hook_event_name", "unknown"))
    tool_name = str(data.get("tool_name", "unknown"))
    if not isinstance(tool_input, dict):
        _history_recorder.append_hook_history(
            HookHistoryEntry(
                hook_event=hook_event,
                script="format_markdown.py",
                status="skipped",
                exit_code=0,
                message="tool_input was not a dict",
                tool_name=tool_name,
            ),
        )
        return 0

    file_paths = _collect_markdown_paths(tool_input)
    if not file_paths:
        _history_recorder.append_hook_history(
            HookHistoryEntry(
                hook_event=hook_event,
                script="format_markdown.py",
                status="skipped",
                exit_code=0,
                message="no markdown targets",
                tool_name=tool_name,
            ),
        )
        return 0

    exit_code = 0
    existing_paths: list[str] = []
    all_violations: list[str] = []
    for file_path in file_paths:
        if Path(file_path).exists():
            existing_paths.append(file_path)
            file_exit_code, violations = _format_markdown_file(file_path)
            exit_code = max(exit_code, file_exit_code)
            if violations:
                all_violations.append(violations)

    message = "\n".join(all_violations) if all_violations else "markdown hook completed"
    _history_recorder.append_hook_history(
        HookHistoryEntry(
            hook_event=hook_event,
            script="format_markdown.py",
            status="success" if exit_code == 0 else "failed",
            exit_code=exit_code,
            target_files=existing_paths,
            message=message,
            tool_name=tool_name,
        ),
    )

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
