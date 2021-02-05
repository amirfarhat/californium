#!/bin/bash

source /proj/MIT-DoS/exp/coap-setup/deps/californium/deter/scripts/config.sh

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

sudo mkdir -p $TMP_DATA

if [[ $TCPDUMP -eq 1 ]]; then
  log "Running origin_server tcpdump...\n"
  screen -d -m sudo $BIN_HOME/run_tcpdump.sh origin_server
fi

if [[ $DO_PERF -eq 1 ]]; then
  log "Running origin_server perf...\n"
  screen -d -m sudo $BIN_HOME/run_perf.sh origin_server
fi

log "Running origin_server...\n"
screen -d -m sudo $BIN_HOME/origin_server_run.sh