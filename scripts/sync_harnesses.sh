#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# sync_harnesses.sh
#
# Mirrors the canonical skill (skills/frontend-studio-gauntlet) into every
# agent harness that ships a "skills/" directory convention:
#
#   .opencode/skills/frontend-studio-gauntlet   -> OpenCode
#   .agents/skills/frontend-studio-gauntlet     -> Universal .agents (Cursor, Codex, ...)
#   .claude/skills/frontend-studio-gauntlet     -> Claude Code
#
# Usage:
#   bash scripts/sync_harnesses.sh           # sync (default)
#   bash scripts/sync_harnesses.sh --check   # verify mirrors match the source
#   bash scripts/sync_harnesses.sh --help    # show this help
#
# Exit codes: 0 success, 1 drift/failure, 2 bad usage.
# ---------------------------------------------------------------------------
set -euo pipefail

SKILL_NAME="frontend-studio-gauntlet"
EXCLUDES=(
  "__pycache__"
  "*.pyc"
  "*.DS_Store"
  "node_modules"
  ".studio"
)

usage() {
  sed -n '2,20p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
}

log() { printf '%s\n' "$*"; }
err() { printf 'error: %s\n' "$*" >&2; }

MODE="sync"
for arg in "$@"; do
  case "$arg" in
    --check) MODE="check" ;;
    -h|--help) usage; exit 0 ;;
    *) err "unknown argument '$arg' (try --help)"; exit 2 ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SOURCE_DIR="${REPO_ROOT}/skills/${SKILL_NAME}"

if [ ! -f "${SOURCE_DIR}/SKILL.md" ]; then
  err "canonical skill not found at ${SOURCE_DIR}/SKILL.md"
  exit 1
fi

TARGETS=(
  "${REPO_ROOT}/.opencode/skills/${SKILL_NAME}"
  "${REPO_ROOT}/.agents/skills/${SKILL_NAME}"
  "${REPO_ROOT}/.claude/skills/${SKILL_NAME}"
)

build_rsync_args() {
  RSYNC_EXCLUDES=(--exclude '__pycache__/' --exclude '*.pyc' --exclude '*.DS_Store' --exclude 'node_modules/' --exclude '.studio/')
}

have_rsync=0
if command -v rsync >/dev/null 2>&1; then
  have_rsync=1
fi

copy_tree() {
  # copy_tree <src_dir> <dest_dir>
  local src="$1" dest="$2"
  mkdir -p "${dest}"
  if [ "${have_rsync}" -eq 1 ]; then
    build_rsync_args
    rsync -a --delete "${RSYNC_EXCLUDES[@]}" "${src}/" "${dest}/"
  else
    rm -rf "${dest:?}"
    mkdir -p "${dest}"
    ( cd "${src}" && tar --exclude='__pycache__' --exclude='*.pyc' --exclude='node_modules' --exclude='.studio' -cf - . ) | ( cd "${dest}" && tar -xf - )
  fi
  # Belt and braces: purge caches that older mirrors may still carry.
  find "${dest}" -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
  find "${dest}" -name '*.pyc' -type f -delete 2>/dev/null || true
}

trees_match() {
  # trees_match <a_dir> <b_dir>
  diff -r -q -x '__pycache__' -x '*.pyc' -x '.DS_Store' "$1" "$2" >/dev/null 2>&1
}

if [ "${MODE}" = "check" ]; then
  status=0
  for dest in "${TARGETS[@]}"; do
    rel="${dest#"${REPO_ROOT}/"}"
    if [ ! -d "${dest}" ]; then
      err "missing mirror: ${rel}"
      status=1
    elif trees_match "${SOURCE_DIR}" "${dest}"; then
      log "up to date: ${rel}"
    else
      err "drifted: ${rel} (run: bash scripts/sync_harnesses.sh)"
      status=1
    fi
  done
  if [ "${status}" -eq 0 ]; then
    log "All harness mirrors match skills/${SKILL_NAME}."
  fi
  exit "${status}"
fi

log "Source: skills/${SKILL_NAME}"
for dest in "${TARGETS[@]}"; do
  rel="${dest#"${REPO_ROOT}/"}"
  copy_tree "${SOURCE_DIR}" "${dest}"
  if trees_match "${SOURCE_DIR}" "${dest}"; then
    log "synced -> ${rel}"
  else
    err "mirror verification failed for ${rel}"
    exit 1
  fi
done

log "Done. ${SKILL_NAME} is live for OpenCode, Claude Code, and universal .agents harnesses."
exit 0
