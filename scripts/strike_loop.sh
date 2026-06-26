#!/usr/bin/env bash
while true; do
    ~/B-Agent/scripts/bb_liquidity_bridge.sh
    ~/B-Agent/scripts/mmi_compiler.sh ~/B-Agent/data/liquidity_depth.log >> ~/B-Agent/data/strike_history.log
    sleep 60
done
