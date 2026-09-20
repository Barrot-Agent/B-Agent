#!/data/data/com.termux/files/usr/bin/bash
set -eu
printf '%s\n' 'BARROT_SELF_GENERATED_BUNDLE_EXECUTED=TRUE'
printf 'TERMUX_SHELL=%s\n' "${SHELL:-unknown}"
printf 'PYTHON=%s\n' "$(python --version 2>&1)"
