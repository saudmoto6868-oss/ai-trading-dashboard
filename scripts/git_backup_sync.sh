#!/usr/bin/env bash
# Local backup + GitHub <-> GitLab sync for the 6868 trading repos (owner 2026-11-20: "if one host is down the other works;
# a backup on this computer, updated every while, not all at once").
#
# 1. BACKUP: one bare repo per project under $BACKUP_DIR, fetching every remote into its own namespace
#    (refs/remotes/<remote>/*). Incremental (only new objects), and never pruned: a branch deleted on a host stays here.
# 2. SYNC (ai-trading-dashboard only), never forced:
#    - GitHub branches -> the GitLab docs mirror (6868-group/ai-trading-dashboard-docs) as "github/<name>" (the prefix that
#      mirror already uses), fast-forward only
#    - GitLab branches (separate history) -> GitHub under "gitlab/<name>", fast-forward only
#    A branch that diverged is skipped and listed in the log; nothing is overwritten.
# Credentials come from the normal git credential helper; this file holds no secret.
# Usage: scripts/git_backup_sync.sh [--no-push]
set -u
BACKUP_DIR="${BACKUP_DIR:-$HOME/Backups/6868-git}"
LOG="$BACKUP_DIR/sync.log"
PUSH=1; [ "${1:-}" = "--no-push" ] && PUSH=0
mkdir -p "$BACKUP_DIR"
log(){ printf '%s %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" | tee -a "$LOG"; }

# project | remote | url
REPOS="
ai-trading-dashboard|github|https://github.com/saudmoto6868-oss/ai-trading-dashboard.git
ai-trading-dashboard|gitlab|https://gitlab.com/6868-group/ai-trading-dashboard.git
ai-trading-dashboard|gitlab_docs|https://gitlab.com/6868-group/ai-trading-dashboard-docs.git
ai-desk|gitlab|https://gitlab.com/6868-group/ai-desk.git
"

echo "$REPOS" | while IFS='|' read -r proj remote url; do
  [ -z "$proj" ] && continue
  repo="$BACKUP_DIR/$proj.git"
  [ -d "$repo" ] || git init -q --bare "$repo"
  if ! git -C "$repo" remote get-url "$remote" >/dev/null 2>&1; then
    git -C "$repo" remote add "$remote" "$url"
  fi
  git -C "$repo" config "remote.$remote.fetch" "+refs/heads/*:refs/remotes/$remote/*"
  git -C "$repo" config "remote.$remote.tagOpt" --no-tags
  if git -C "$repo" fetch -q "$remote" 2>>"$LOG"; then
    log "backup $proj/$remote: $(git -C "$repo" for-each-ref --format=x "refs/remotes/$remote" | wc -l | tr -d ' ') branches"
  else
    log "backup $proj/$remote: FETCH FAILED (host down or no access) - kept the last copy"
  fi
done

[ "$PUSH" = 1 ] || { log "sync skipped (--no-push)"; exit 0; }
repo="$BACKUP_DIR/ai-trading-dashboard.git"
push_ff(){   # $1 = target remote, $2.. = refspecs; non-forced, so a diverged branch is rejected (logged), never overwritten
  local target="$1"; shift
  local out; out=$(git -C "$repo" push --porcelain "$target" "$@" 2>&1)
  local ok rej; ok=$(printf '%s\n' "$out" | grep -c $'^[* ]\t'); rej=$(printf '%s\n' "$out" | grep -c $'^!\t')
  log "sync -> $target: $ok new/updated, $rej rejected (diverged or protected)"
  printf '%s\n' "$out" | grep '^!' | head -20 >>"$LOG"
}
specs_for(){   # $1 = source remote, $2 = target prefix -> refspecs on stdout (bash 3.2 on macOS has no mapfile)
  git -C "$repo" for-each-ref --format='%(refname:strip=3)' "refs/remotes/$1" | while read -r b; do
    [ "$b" = HEAD ] || printf 'refs/remotes/%s/%s:refs/heads/%s%s\n' "$1" "$b" "$2" "$b"; done
}
# GitHub -> GitLab docs mirror under github/<name>; GitLab -> GitHub under gitlab/<name>
specs=$(specs_for github "github/"); [ -n "$specs" ] && push_ff gitlab_docs $specs
specs=$(specs_for gitlab "gitlab/"); [ -n "$specs" ] && push_ff github $specs
log "done"
