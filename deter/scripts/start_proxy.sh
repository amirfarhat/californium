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
sudo chmod 777 $TMP_DATA

if [[ $TCPDUMP -eq 1 ]]; then
  log "Running proxy tcpdump...\n"
  screen -d -m sudo $BIN_HOME/run_tcpdump.sh proxy
fi

if [[ $PROXY_TOP -eq 1 ]]; then
  log "Running proxy top...\n"
  screen -d -m sudo $BIN_HOME/top.sh
fi

if [[ $DO_PERF -eq 1 ]]; then
  log "Running proxy perf...\n"
  screen -d -m sudo $BIN_HOME/run_perf.sh proxy
fi

log "Running proxy...\n"
screen -d -m sudo $BIN_HOME/proxy_run.sh