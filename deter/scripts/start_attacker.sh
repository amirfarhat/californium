#!/bin/bash

source ./config.sh
source ./setup.sh

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

if [[ $TCPDUMP -eq 1 ]]; then
  log "Running attacker_tcpdump...\n"
  screen -d -m sudo $BIN_HOME/attacker_tcpdump.sh
fi

log "Running attacker_flood...\n"
screen -d -m $BIN_HOME/attacker_flood.sh