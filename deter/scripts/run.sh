
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
