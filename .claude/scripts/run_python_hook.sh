#!/usr/bin/env bash
# Wrapper that finds the appropriate Python interpreter and runs a Python hook.
# Usage: run_python_hook.sh <path/to/hook.py>
# stdin (JSON hook payload) is forwarded to the Python script.
#
# Resolution order:
#   1. .venv/Scripts/python.exe  (Windows hooks venv)
#   2. .venv/bin/python          (Unix hooks venv)
#   3. python3
#   4. python
#   5. exit 0 silently (Python unavailable — hook is skipped gracefully)

SCRIPT="${1:-}"
if [[ -z "$SCRIPT" ]]; then
    echo "Usage: run_python_hook.sh <script.py>" >&2
    exit 1
fi

INPUT=$(cat)
SCRIPTS_ROOT=".claude/scripts"

SCRIPT_REL="${SCRIPT#./}"
SCRIPT_REL="${SCRIPT_REL#${SCRIPTS_ROOT}/}"
MODULE_PATH="${SCRIPT_REL%.py}"
MODULE_PATH="${MODULE_PATH//\//.}"

run_hook() {
    if [[ -n "${PYTHONPATH:-}" ]]; then
        printf '%s' "$INPUT" | PYTHONUTF8=1 PYTHONPATH="$SCRIPTS_ROOT:$PYTHONPATH" "$@" -m "$MODULE_PATH"
        return
    fi

    printf '%s' "$INPUT" | PYTHONUTF8=1 PYTHONPATH="$SCRIPTS_ROOT" "$@" -m "$MODULE_PATH"
}

if [[ -f ".venv/Scripts/python.exe" ]]; then
    run_hook ".venv/Scripts/python.exe"
elif [[ -f ".venv/bin/python" ]]; then
    run_hook ".venv/bin/python"
elif command -v python3 &>/dev/null; then
    run_hook python3
elif command -v python &>/dev/null; then
    run_hook python
else
    # No Python available — skip hook gracefully
    exit 0
fi
