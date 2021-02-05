#!/bin/bash

source /proj/MIT-DoS/exp/coap-setup/deps/californium/deter/scripts/config.sh

node_type=$1

if [ $node_type = "proxy" ]; then
  PERF_NAME=$PROXY_PERF

elif [ $node_type = "attacker" ]; then
  PERF_NAME=$ATTACKER_PERF

elif [ $node_type = "origin_server" ]; then
  PERF_NAME=$ORIGIN_SERVER_PERF

else
  echo "Unknown parameter"
  exit 1
fi

sudo timeout $PROXY_DURATION perf record -F $PERF_FREQUENCY -a -g -o $TMP_DATA/$PERF_NAME