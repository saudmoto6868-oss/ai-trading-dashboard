#!/bin/sh
# Start the XPiX Agent HTTP server on the Mac (127.0.0.1 only). The token comes from the environment or from ~/.xpix_agent_token (created once, chmod 600).
cd "$(dirname "$0")/../.." || exit 1
T="$HOME/.xpix_agent_token"
if [ -z "$XPIX_AGENT_TOKEN" ]; then [ -f "$T" ] || { umask 077; openssl rand -hex 24 > "$T"; echo "New token saved to $T (put the same value in n8n's credentials; never paste it in chat)."; }; XPIX_AGENT_TOKEN="$(cat "$T")"; export XPIX_AGENT_TOKEN; fi
exec node tools/xpix_agent/server.js --out "$HOME/xpix_out" --url "${XPIX_URL:-http://localhost:8501}"
