#!/data/data/com.termux/files/usr/bin/bash
set -eu

printf '%s\n' 'BARROT_AUTONOMOUS_SELF_DROP=TRUE'
printf 'BARROT_TASK_ID=%s\n' 'controller_real_tool_call'
printf 'BARROT_ACTION=%s\n' 'SELF_DROP_PROBE'
printf 'BARROT_EXECUTED_AT=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
printf '%s\n' 'BARROT_AUTONOMOUS_SELF_DROP_COMPLETE=TRUE'
