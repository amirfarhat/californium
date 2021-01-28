
. /proj/MIT-DoS/exp/coap-setup/deps/californium/deter/scripts/config.sh

# Options
while getopts ":v" opt; do
  case "$opt" in
    "v") _V=1;;
  esac
done

# Debug printer
function log () {
  if [[ $_V -eq 1 ]]; then
    printf "$@"
  fi
}

# Origin server
log "[SETUP] Starting origin server...\n"
ssh $RUN_USER@$PROXY_NAME "$SCRIPTS_HOME/start_origin_server.sh -v"

# Proxy
log "[SETUP] Starting proxy...\n"
ssh $RUN_USER@$PROXY_NAME "$SCRIPTS_HOME/start_proxy.sh -v"

# Attacker
log "[SETUP] Starting attackers...\n"
ssh $RUN_USER@$ATTACKER_NAME "$SCRIPTS_HOME/start_attacker.sh -v"

sleep 15
