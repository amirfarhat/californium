
. /proj/MIT-DoS/exp/coap-setup/deps/californium/deter/scripts/config.sh

# Options
while getopts ":vn:" opt; do
  case "$opt" in
    "v") _V=1;;
    "n") n=$OPTARG;;
  esac
done

# Debug printer
function log () {
  if [[ $_V -eq 1 ]]; then
    printf "$@"
  fi
}

mkdir -p $TMP_DATA
mkdir -p $DETER_HOME/expdata/real/$n
data_dir=$DETER_HOME/expdata/real/$n
log "Created data directory $data_dir\n"

# Kill all detached remote sessions
for host_name in ${HOST_NAMES[@]}; do
  log "Killing detached sessions on $host_name...\n"
  ssh $RUN_USER@$host_name "$BIN_HOME/kill_detached.sh"
  log "OK\n"
done

# Origin server
log "[SETUP] Starting origin server...\n"
ssh $RUN_USER@$PROXY_NAME "$SCRIPTS_HOME/start_origin_server.sh -v"
log "OK\n"

# Proxy
log "[SETUP] Starting proxy...\n"
ssh $RUN_USER@$PROXY_NAME "$SCRIPTS_HOME/start_proxy.sh -v"
log "OK\n"

log "Sleeping for a bit...\n"
sleep 5
log "OK\n"

# Attacker
log "[SETUP] Starting attackers...\n"
ssh $RUN_USER@$ATTACKER_NAME "$SCRIPTS_HOME/start_attacker.sh -v"
log "OK\n"

sleep_amt=$(( $PROXY_DURATION ))
log "[SETUP] Waiting for $sleep_amt seconds...\n"
sleep $sleep_amt
log "OK\n"

# Move data files from tmp into the data directory
for host_name in ${HOST_NAMES[@]}; do
  log "Moving data from $host_name to $data_dir...\n"
  ssh $RUN_USER@$host_name "$BIN_HOME/move_data.sh $data_dir"
  log "OK\n"
done

log "Finished experiment!\n"
