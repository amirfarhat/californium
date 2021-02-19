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

OPLOG=$TMP_DATA/proxy_ops.log
sudo touch $OPLOG

if [[ $TCPDUMP -eq 1 ]]; then
  log "Running proxy tcpdump...\n"
  sudo screen -c $UTILS_HOME/oplog.conf -d -m -L -Logfile $OPLOG sudo $BIN_HOME/run_tcpdump.sh proxy

fi

if [[ $PROXY_TOP -eq 1 ]]; then
  log "Running proxy top...\n"
  sudo screen -c $UTILS_HOME/oplog.conf -d -m -L -Logfile $OPLOG sudo $BIN_HOME/top.sh
  
fi

log "Running proxy...\n"
sudo screen -c $UTILS_HOME/oplog.conf -d -m -L -Logfile $OPLOG sudo $BIN_HOME/proxy_run.sh
