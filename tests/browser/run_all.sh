#!/bin/sh
# Runs every tests/browser/*_mock.js with the right input (a few need a special build / page). Usage: sh tests/browser/run_all.sh   (needs playwright: NODE_PATH=$(npm root -g))
# Prints PASS / FAIL per test and exits 1 if any failed.
set -u; cd "$(dirname "$0")/../.."; export NODE_PATH="${NODE_PATH:-$(npm root -g)}"; T=${TMPDIR:-/tmp}/xpix_ws; mkdir -p "$T"
python3 -c "from modules.workspace import build_workspace_html as b; open('$T/ws.html','w').write(b(['BTC-USDT','ETH-USDT'])); open('$T/ws_gold.html','w').write(b(['BTC-USDT','HL:xyz:GOLD']))" || exit 1
FOOTPRINT_SERVER_URL=https://rec.example.test python3 -c "import sys; sys.path.insert(0,'.'); from modules.workspace import build_workspace_html as b; open('$T/ws_fp.html','w').write(b(['BTC-USDT']))" || exit 1
python3 -c "
import sys; sys.path.insert(0,'.')
from modules.workspace import build_workspace_html as b
from modules import intermarket as IM
ev=[{'id':'x','a':'BTC-USDT','b':'ETH-USDT','inverse':False,'tf':'1h','direction':'bullish','bars_ago':2,'t':'2026-11-06T10:00:00+00:00','session':'London','p1':1,'p2':2,'a_name':'Bitcoin','b_name':'Ethereum','a_color':'#f7931a','b_color':'#8c9eff','text_en':'SMT up on 1H between Bitcoin and Ethereum','text_ar':'x','series_a':[1]*60,'series_b':[1]*60}]
open('$T/ws_smt.html','w').write(b(['BTC-USDT','ETH-USDT'], smt=IM.chips(ev)))" || exit 1
ls tests/browser/*_mock.js | xargs -P 6 -I{} sh -c 'f={}; case $f in
  *standard_layout_mock.js) a='$T'/ws_gold.html;;   # needs the gold symbol in the symbol list
  *footprint_recorder_client_mock.js) a='$T'/ws_fp.html;;   # needs a build with FOOTPRINT_SERVER_URL set
  *smt_strip_mock.js) a='$T'/ws_smt.html;;   # needs a build with SMT chips
  *montecarlo_pvalue_mock.js) a=modules/montecarlo_app.html;;   # a different page
  *) a='$T'/ws.html;; esac; timeout 150 node $f $a >/dev/null 2>&1 && echo "PASS $f" || echo "FAIL $f"' | sort > "$T/result.txt"
grep -c PASS "$T/result.txt"; grep FAIL "$T/result.txt"; ! grep -q FAIL "$T/result.txt"
