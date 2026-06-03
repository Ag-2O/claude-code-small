"""Deterministic CLI/DAO for the shared ``.artifacts/state.db`` SQLite database.

This tool owns all structured access to the workflow state database so that the
probabilistic LLM never edits raw state by hand. A single database under the
artifacts root holds the state for every feature, keyed by feature name. Task
identifiers follow the ``task_<phase>_<task_no>`` convention (e.g. ``task_1_1``)
and are decomposed into integer ``phase`` / ``task_no`` columns so that
per-phase queries (summaries, reviews) are cheap.

Schema::

    features(feature PK, current_phase INT, updated_at TEXT)
    tasks(feature, phase INT, task_no INT, status TEXT, updated_at TEXT,
          PK(feature, phase, task_no))
    blockers(id PK, feature, text TEXT, created_at TEXT)

Progress is never stored; it is recomputed from ``tasks`` on every read.

Run ``uv run python state_dao.py --help`` for the available subcommands.
"""

import argparse
import datetime
import re
import sqlite3
import sys
from collections.abc import Iterable, Iterator
from contextlib import closing, contextmanager
from dataclasses import dataclass
from pathlib import Path

_VALID_STATUSES = ("todo", "in_progress", "blocked", "done")
_DEFAULT_ROOT = ".artifacts"
_DB_NAME = "state.db"
_TASK_PATTERN = re.compile(r"^task_(\d+)_(\d+)$", re.IGNORECASE)
_PHASE_PATTERN = re.compile(r"^(?:phase_)?(\d+)$", re.IGNORECASE)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS features (
    feature       TEXT PRIMARY KEY,
    current_phase INTEGER NOT NULL DEFAULT 1,
    updated_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tasks (
    feature    TEXT NOT NULL,
    phase      INTEGER NOT NULL,
    task_no    INTEGER NOT NULL,
    status     TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (feature, phase, task_no),
    FOREIGN KEY (feature) REFERENCES features(feature) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS blockers (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    feature    TEXT NOT NULL,
    text       TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (feature) REFERENCES features(feature) ON DELETE CASCADE
);
"""


@dataclass(frozen=True)
class Task:
    """A single task row.

    Attributes:
        phase: Phase number (the ``<phase>`` in ``task_<phase>_<task_no>``).
        task_no: Task number within the phase.
        status: One of :data:`_VALID_STATUSES`.

    """

    phase: int
    task_no: int
    status: str

    @property
    def task_id(self) -> str:
        """Return the canonical ``task_<phase>_<task_no>`` identifier."""
        return format_task(self.phase, self.task_no)


def _today() -> str:
    """Return today's local date as an ISO ``YYYY-MM-DD`` string."""
    return datetime.date.today().isoformat()


def parse_task(token: str) -> tuple[int, int]:
    """Split a ``task_<phase>_<task_no>`` token into integers.

    Args:
        token: Task identifier such as ``task_1_2`` (case-insensitive).

    Returns:
        A ``(phase, task_no)`` tuple.

    Raises:
        ValueError: If the token does not match the expected pattern.

    """
    match = _TASK_PATTERN.match(token.strip())
    if not match:
        raise ValueError(
            f"invalid task id '{token}' (expected task_<phase>_<task_no>)",
        )
    return int(match.group(1)), int(match.group(2))


def format_task(phase: int, task_no: int) -> str:
    """Build the canonical task identifier from its parts."""
    return f"task_{phase}_{task_no}"


def parse_phase(token: str) -> int:
    """Parse a ``phase_<n>`` or bare ``<n>`` token into an integer.

    Args:
        token: Phase identifier such as ``phase_2`` or ``2``.

    Returns:
        The phase number.

    Raises:
        ValueError: If the token does not match the expected pattern.

    """
    match = _PHASE_PATTERN.match(token.strip())
    if not match:
        raise ValueError(f"invalid phase '{token}' (expected phase_<n> or <n>)")
    return int(match.group(1))


def format_phase(phase: int) -> str:
    """Build the canonical ``phase_<n>`` identifier."""
    return f"phase_{phase}"


def _db_path(root: Path) -> Path:
    """Return the database path for an artifacts root."""
    return root / _DB_NAME


@contextmanager
def _connect(root: Path) -> Iterator[sqlite3.Connection]:
    """Open the state database, creating its parent and schema as needed.

    Args:
        root: Artifacts root directory.

    Yields:
        An open connection with foreign keys enabled. Commits on success.

    """
    path = _db_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(path)) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript(_SCHEMA)
        yield conn
        conn.commit()


def _feature_exists(conn: sqlite3.Connection, feature: str) -> bool:
    """Return whether a feature row exists."""
    row = conn.execute(
        "SELECT 1 FROM features WHERE feature = ?",
        (feature,),
    ).fetchone()
    return row is not None


def _require_feature(conn: sqlite3.Connection, feature: str) -> None:
    """Raise if a feature has not been initialized.

    Raises:
        ValueError: If the feature row does not exist.

    """
    if not _feature_exists(conn, feature):
        raise ValueError(f"feature '{feature}' not initialized (run init first)")


def _load_tasks(
    conn: sqlite3.Connection,
    feature: str,
    *,
    phase: int | None = None,
    status: str | None = None,
) -> list[Task]:
    """Load tasks for a feature ordered by phase then task number.

    Args:
        conn: Open connection.
        feature: Feature name.
        phase: Optional phase filter.
        status: Optional status filter.

    Returns:
        Matching tasks in deterministic order.

    """
    query = "SELECT phase, task_no, status FROM tasks WHERE feature = ?"
    params: list[object] = [feature]
    if phase is not None:
        query += " AND phase = ?"
        params.append(phase)
    if status is not None:
        query += " AND status = ?"
        params.append(status)
    query += " ORDER BY phase, task_no"
    rows = conn.execute(query, params).fetchall()
    return [Task(row["phase"], row["task_no"], row["status"]) for row in rows]


def _progress(tasks: Iterable[Task]) -> tuple[int, int, int]:
    """Return ``(done, total, percent)`` for a task collection."""
    tasks = list(tasks)
    total = len(tasks)
    done = sum(1 for task in tasks if task.status == "done")
    percent = round(done * 100 / total) if total else 0
    return done, total, percent


def _render(
    feature: str,
    current_phase: int,
    tasks: list[Task],
    blockers: list[str],
) -> str:
    """Render a human-readable view of a feature's state.

    Args:
        feature: Feature name.
        current_phase: Current phase number.
        tasks: Tasks ordered by phase then task number.
        blockers: Open blocker descriptions.

    Returns:
        A Markdown-flavored text block for terminal display.

    """
    done, total, percent = _progress(tasks)
    lines = [
        f"# 進捗: {feature}",
        "",
        f"- 現在フェーズ: {format_phase(current_phase)}",
        f"- 進捗: {done}/{total} ({percent}%)",
        "",
        "| タスク | 状態 |",
        "| --- | --- |",
    ]
    lines.extend(f"| {task.task_id} | {task.status} |" for task in tasks)
    lines.extend(["", "## ブロッカー", ""])
    if blockers:
        lines.extend(f"- {blocker}" for blocker in blockers)
    else:
        lines.append("- なし")
    return "\n".join(lines)


def _load_blockers(conn: sqlite3.Connection, feature: str) -> list[str]:
    """Return open blocker descriptions for a feature in insertion order."""
    rows = conn.execute(
        "SELECT text FROM blockers WHERE feature = ? ORDER BY id",
        (feature,),
    ).fetchall()
    return [row["text"] for row in rows]


def _current_phase(conn: sqlite3.Connection, feature: str) -> int:
    """Return the stored current phase for a feature."""
    row = conn.execute(
        "SELECT current_phase FROM features WHERE feature = ?",
        (feature,),
    ).fetchone()
    return int(row["current_phase"])


def _cmd_init(args: argparse.Namespace) -> int:
    """Create a feature row if it does not already exist."""
    phase = parse_phase(args.phase)
    with _connect(Path(args.root)) as conn:
        if _feature_exists(conn, args.feature):
            print(f"feature already exists: {args.feature}")
            return 0
        conn.execute(
            "INSERT INTO features (feature, current_phase, updated_at) "
            "VALUES (?, ?, ?)",
            (args.feature, phase, _today()),
        )
    print(f"created feature '{args.feature}' at {format_phase(phase)}")
    return 0


def _cmd_set_task(args: argparse.Namespace) -> int:
    """Upsert the status of a single task."""
    phase, task_no = parse_task(args.task)
    with _connect(Path(args.root)) as conn:
        _require_feature(conn, args.feature)
        conn.execute(
            "INSERT INTO tasks (feature, phase, task_no, status, updated_at) "
            "VALUES (?, ?, ?, ?, ?) "
            "ON CONFLICT(feature, phase, task_no) "
            "DO UPDATE SET status = excluded.status, updated_at = excluded.updated_at",
            (args.feature, phase, task_no, args.status, _today()),
        )
        conn.execute(
            "UPDATE features SET updated_at = ? WHERE feature = ?",
            (_today(), args.feature),
        )
        _, _, percent = _progress(_load_tasks(conn, args.feature))
    print(f"{format_task(phase, task_no)} -> {args.status} (progress {percent}%)")
    return 0


def _cmd_set_phase(args: argparse.Namespace) -> int:
    """Update the current phase of a feature."""
    phase = parse_phase(args.phase)
    with _connect(Path(args.root)) as conn:
        _require_feature(conn, args.feature)
        conn.execute(
            "UPDATE features SET current_phase = ?, updated_at = ? WHERE feature = ?",
            (phase, _today(), args.feature),
        )
    print(f"current_phase -> {format_phase(phase)}")
    return 0


def _cmd_add_blocker(args: argparse.Namespace) -> int:
    """Append a blocker description to a feature."""
    with _connect(Path(args.root)) as conn:
        _require_feature(conn, args.feature)
        conn.execute(
            "INSERT INTO blockers (feature, text, created_at) VALUES (?, ?, ?)",
            (args.feature, args.text, _today()),
        )
        count = len(_load_blockers(conn, args.feature))
    print(f"blocker added ({count} open)")
    return 0


def _cmd_clear_blockers(args: argparse.Namespace) -> int:
    """Remove all open blockers for a feature."""
    with _connect(Path(args.root)) as conn:
        _require_feature(conn, args.feature)
        conn.execute("DELETE FROM blockers WHERE feature = ?", (args.feature,))
    print("blockers cleared")
    return 0


def _cmd_show(args: argparse.Namespace) -> int:
    """Print a human-readable view of a feature's state."""
    with _connect(Path(args.root)) as conn:
        _require_feature(conn, args.feature)
        text = _render(
            args.feature,
            _current_phase(conn, args.feature),
            _load_tasks(conn, args.feature),
            _load_blockers(conn, args.feature),
        )
    print(text)
    return 0


def _cmd_list_tasks(args: argparse.Namespace) -> int:
    """Print matching task ids, one per line, for scripting."""
    phase = parse_phase(args.phase) if args.phase else None
    with _connect(Path(args.root)) as conn:
        _require_feature(conn, args.feature)
        tasks = _load_tasks(conn, args.feature, phase=phase, status=args.status)
    for task in tasks:
        print(task.task_id)
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    """Validate that a feature exists and all task statuses are valid."""
    with _connect(Path(args.root)) as conn:
        if not _feature_exists(conn, args.feature):
            print(f"invalid: feature '{args.feature}' not found", file=sys.stderr)
            return 1
        for task in _load_tasks(conn, args.feature):
            if task.status not in _VALID_STATUSES:
                print(
                    f"invalid: {task.task_id} has status '{task.status}'",
                    file=sys.stderr,
                )
                return 1
    print("valid")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    """Build the argument parser with all subcommands."""
    parser = argparse.ArgumentParser(
        description="Manage the shared .artifacts/state.db workflow database.",
    )
    parser.add_argument(
        "--root",
        default=_DEFAULT_ROOT,
        help=f"artifacts root directory (default: {_DEFAULT_ROOT})",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="create a feature row")
    init.add_argument("--feature", required=True)
    init.add_argument("--phase", default="phase_1")
    init.set_defaults(func=_cmd_init)

    set_task = sub.add_parser("set-task", help="set a task status")
    set_task.add_argument("--feature", required=True)
    set_task.add_argument("--task", required=True, help="task id, e.g. task_1_1")
    set_task.add_argument("--status", required=True, choices=_VALID_STATUSES)
    set_task.set_defaults(func=_cmd_set_task)

    set_phase = sub.add_parser("set-phase", help="set the current phase")
    set_phase.add_argument("--feature", required=True)
    set_phase.add_argument("--phase", required=True, help="phase id, e.g. phase_2")
    set_phase.set_defaults(func=_cmd_set_phase)

    add_blocker = sub.add_parser("add-blocker", help="append a blocker")
    add_blocker.add_argument("--feature", required=True)
    add_blocker.add_argument("--text", required=True)
    add_blocker.set_defaults(func=_cmd_add_blocker)

    clear_blockers = sub.add_parser("clear-blockers", help="remove all blockers")
    clear_blockers.add_argument("--feature", required=True)
    clear_blockers.set_defaults(func=_cmd_clear_blockers)

    show = sub.add_parser("show", help="print a feature's state")
    show.add_argument("--feature", required=True)
    show.set_defaults(func=_cmd_show)

    list_tasks = sub.add_parser("list-tasks", help="print matching task ids")
    list_tasks.add_argument("--feature", required=True)
    list_tasks.add_argument("--status", choices=_VALID_STATUSES)
    list_tasks.add_argument("--phase", help="phase filter, e.g. phase_1")
    list_tasks.set_defaults(func=_cmd_list_tasks)

    validate = sub.add_parser("validate", help="validate a feature's state")
    validate.add_argument("--feature", required=True)
    validate.set_defaults(func=_cmd_validate)

    return parser


def _configure_stdio_encoding() -> None:
    """Force ``stdout`` / ``stderr`` to UTF-8 to avoid mojibake on Windows.

    On Windows the default console encoding is often cp932 (Shift_JIS), which
    cannot represent the Japanese characters used in the rendered output.
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="replace")


def main(argv: list[str] | None = None) -> int:
    """Entry point for the state database CLI.

    Args:
        argv: Optional argument vector. Defaults to ``sys.argv[1:]``.

    Returns:
        Process exit code.

    """
    _configure_stdio_encoding()
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (ValueError, sqlite3.Error) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
