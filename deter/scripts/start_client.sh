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
  log "Running client tcpdump...\n"
  screen -d -m sudo $BIN_HOME/run_tcpdump.sh client
fi

log "Running client...\n"
screen -d -m sudo $BIN_HOME/client_run.sh