#!/bin/bash
# 检查选定脚本；单项失败后继续，最后返回汇总状态。
set -uo pipefail

if (( $# > 1 )); then
    echo "Usage: bash check.sh [file-or-directory]" >&2
    exit 2
fi

selection=$(mktemp) || exit 2
trap 'rm -f "$selection"' EXIT
if (( $# == 1 )); then
    if [[ -f "$1" ]]; then
        printf '%s\0' "$1" > "$selection"
    elif [[ -d "$1" ]]; then
        find "$1" -type f -name '*.sh' -print0 > "$selection" || exit 2
    else
        printf 'Target does not exist: %s\n' "$1" >&2
        exit 2
    fi
else
    root=$(git rev-parse --show-toplevel 2>/dev/null) || {
        echo "Not in a Git repository; provide a file or directory." >&2
        exit 2
    }
    cd "$root" || exit 2
    git ls-files --cached --others --exclude-standard --deduplicate -z -- '*.sh' > "$selection" || exit 2
fi

has_shellcheck=1
if ! command -v shellcheck >/dev/null 2>&1; then
    echo "SKIPPED shellcheck: command is not installed." >&2
    has_shellcheck=0
fi

total=0
syntax_failed=0
static_failed=0
while IFS= read -r -d '' file; do
    [[ -f "$file" ]] || continue
    total=$((total + 1))
    if bash -n -- "$file"; then
        printf 'PASS syntax: %s\n' "$file"
    else
        syntax_failed=$((syntax_failed + 1))
    fi
    if (( has_shellcheck )); then
        if shellcheck -x -- "$file"; then
            printf 'PASS shellcheck: %s\n' "$file"
        else
            static_failed=$((static_failed + 1))
        fi
    fi
done < "$selection"

printf 'Files: %s; syntax failures: %s; shellcheck failures: %s; shellcheck skipped: %s\n' \
    "$total" "$syntax_failed" "$static_failed" "$((total * (1 - has_shellcheck)))"
if (( total == 0 )); then
    echo "No existing Shell files were selected." >&2
    exit 2
fi
(( has_shellcheck && syntax_failed == 0 && static_failed == 0 ))
