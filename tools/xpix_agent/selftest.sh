#!/bin/sh
# One-command check of the XPiX Agent on YOUR Mac (live data, real browser). Prints PASS / FAIL per step; nothing is traded or changed except the chart's symbol / timeframe.
# Needs: the platform running (streamlit run main.py), and  npm i playwright && npx playwright install chromium
# Usage:  sh tools/xpix_agent/selftest.sh [URL]      (default http://localhost:8501)
cd "$(dirname "$0")/../.." || exit 1; URL="${1:-http://localhost:8501}"; A="node tools/xpix_agent/xpix_agent.js --url $URL"; F=0
step() { name="$1"; shift; out="$("$@" 2>&1)"; if echo "$out" | grep -q '"ok":false\|Error\|not found'; then echo "FAIL  $name  -> $(echo "$out" | head -c 200)"; F=1; else echo "PASS  $name"; fi; }
step "pages"            $A pages
step "page workspace"   $A page workspace
step "state"            $A state
step "tf 15m"           $A tf 15m
step "symbol (gold)"    $A symbol HL:xyz:GOLD
step "symbol (BTC)"     $A symbol BTC-USDT
step "toggle msb on"    $A toggle msb on
step "set msb fib 0.3"  $A set msb fib 0.3
step "draw hline"       $A draw '{"kind":"hline","price":1}'
step "cleardrawings"    $A cleardrawings
step "screenshot"       $A shot --out /tmp/xpix_selftest.png
step "page radar"       $A page radar
step "page workspace"   $A page workspace
echo "Screenshot: /tmp/xpix_selftest.png   (If 'symbol (gold)' fails, the symbol is not in this platform's list: run '$A state' and read sym.)"
exit $F
