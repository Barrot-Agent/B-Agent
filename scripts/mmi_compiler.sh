#!/usr/bin/env bash
FILE=$1
if [[ ! -f "$FILE" ]]; then
    printf "SIGNAL: NULL_DATA\n"
    exit 1
fi

# Use awk for floating-point arithmetic (Pure Bash compatibility)
AVG=$(grep -oE '[0-9.]+' "$FILE" | awk '{sum+=$1; n++} END {if (n > 0) print sum/n; else print 0}')

if (( $(echo "$AVG > 0" | bc -l) )); then
    printf "SIGNAL: STRIKE_READY | AVG_BID: %.4f\n" "$AVG"
else
    printf "SIGNAL: NULL_LIQUIDITY\n"
fi
