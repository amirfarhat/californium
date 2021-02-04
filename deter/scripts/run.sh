#!/bin/bash

source /proj/MIT-DoS/exp/coap-setup/deps/californium/deter/scripts/config.sh

# Options
while getopts ":vn:x:" opt; do
  case "$opt" in
    "v") _V=1;;
    "n") _N=$OPTARG;;
    "x") _EXP_NAME=$OPTARG;;
  esac
done

# Check options
if [[ $_N -le 0 ]]; then
  echo "Expect positive number of runs"
  exit 1
fi
if [[ -z $_EXP_NAME ]]; then
  echo "Expect nonempty experiment name"
  exit 1
fi


# Debug printer
function log () {
  if [[ $_V -eq 1 ]]; then
    printf "$@"
  fi
}

log "[CHECKPOINT] Starting experiment $_EXP_NAME\n"
log "[CHECKPOINT] Running $_N trials\n"

# Create experiment's data directory
experiment_dir=$DETER_HOME/expdata/real/proxy/$_EXP_NAME
mkdir -p $experiment_dir
log "[CHECKPOINT] Created experiment directory $experiment_dir\n"

# Create experiment runs' data directories
for ((i=1; i<=$_N; i++)); do
  run_data_dir="$experiment_dir/$i"
  log "Creating $run_data_dir ...\n"
  mkdir -p $run_data_dir
done
log "[CHECKPOINT] Created experiment run directories\n"

# Launch experiment runs sequentially
for ((i=1; i<=$_N; i++)); do
  log "[CHECKPOINT] Starting experiment trial $i\n"
  run_data_dir="$experiment_dir/$i"

  # Kill all detached remote sessions
  for host_name in ${HOST_NAMES[@]}; do
    log "[SETUP] Killing detached sessions on $host_name...\n"
    ssh $RUN_USER@$host_name "sudo $BIN_HOME/kill_detached.sh"
    log "OK\n"
  done

  # Run setup script just in case
  for host_name in ${HOST_NAMES[@]}; do
    log "[SETUP] Running setup script on $host_name...\n"
    ssh $RUN_USER@$host_name "sudo $SCRIPTS_DIR/node_setup.sh"
    log "OK\n"
  done

  # Origin server
  log "[LAUNCH] Starting origin server...\n"
  ssh $RUN_USER@$ORIGIN_SERVER_NAME "sudo $SCRIPTS_HOME/start_origin_server.sh -v"
  log "OK\n"

  # Proxy
  log "[LAUNCH] Starting proxy...\n"
  ssh $RUN_USER@$PROXY_NAME "sudo $SCRIPTS_HOME/start_proxy.sh -v"
  log "OK\n"

  log "[SETUP] Sleeping for a bit...\n"
  sleep 5
  log "OK\n"

  # Attacker
  log "[LAUNCH] Starting attackers...\n"
  ssh $RUN_USER@$ATTACKER_NAME "sudo $SCRIPTS_HOME/start_attacker.sh -v"
  log "OK\n"

  # Inline countdown timer
  sleep_amt=$(( $PROXY_DURATION ))
  log "[SETUP] Waiting for $sleep_amt seconds...\n"
  secs=$sleep_amt
  while [ $secs -gt 0 ]; do
    echo -ne "$secs\033[0K\r"
    sleep 1
    : $((secs--))
  done
  log "OK\n"

  # Move data files from tmp into the corresponding data run directory
  for host_name in ${HOST_NAMES[@]}; do
    log "[CHECKPOINT] Moving data from $host_name to $run_data_dir...\n"
    ssh $RUN_USER@$host_name "sudo $BIN_HOME/move_data.sh $run_data_dir"
    log "OK\n"
  done
done

# Zip experiment directory for super fast network transfer
log "[SETUP] Zipping data files...\n"
zip -r $experiment_dir.zip $experiment_dir
log "OK\n"

log "[CHECKPOINT] Finished experiment!\n"
