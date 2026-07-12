#!/usr/bin/env bash
# PostToolUse hook: fires after every Edit/Write tool call.
# Filters down to retrieval-relevant files, then triggers the eval-runner
# subagent so retrieval quality gets measured on every meaningful change --
# deterministically, not "whenever I remember to run the eval script."
set -euo pipefail

# Claude Code pipes a JSON payload describing the tool call on stdin.
INPUT_JSON="$(cat)"

# Pull the edited file path out of the payload. Requires jq; if you don't
# have it: `brew install jq` / `apt install jq`.
FILE_PATH="$(echo "$INPUT_JSON" | jq -r '.tool_input.file_path // empty')"

if [[ -z "$FILE_PATH" ]]; then
  exit 0
fi

# Only fire for the files that actually own chunking / embedding / FAISS
# retrieval logic in this repo -- NOT every file edit.
case "$FILE_PATH" in
  *app/core/knowledge/agent.py|*app/core/knowledge/html_extractor.py)
    ;;
  *)
    exit 0
    ;;
esac

LOG_DIR="$CLAUDE_PROJECT_DIR/eval_results"
mkdir -p "$LOG_DIR"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
LOG_FILE="$LOG_DIR/eval-trigger-${TIMESTAMP}.log"

echo "[hook] Retrieval-relevant file changed: $FILE_PATH" >> "$LOG_FILE"
echo "[hook] Delegating to eval-runner subagent..." >> "$LOG_FILE"

# Explicit subagent invocation via headless (-p / print) mode, backgrounded
# so it doesn't block your main session. NOTE: verify the exact headless
# invocation flags against your installed Claude Code version
# (`claude -p --help`) before relying on this in a live demo -- CLI flags
# for headless mode have changed across recent releases.
nohup claude -p "@eval-runner Run a retrieval evaluation now. The file $FILE_PATH was just edited. Report metric deltas, likely cause, and one next action." \
  >> "$LOG_FILE" 2>&1 &

echo "[hook] eval-runner triggered in background, logging to $LOG_FILE" >> "$LOG_FILE"

# Always exit 0: this hook informs and logs, it never blocks the edit.
exit 0
