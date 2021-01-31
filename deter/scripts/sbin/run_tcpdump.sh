#!/bin/bash

. /proj/MIT-DoS/exp/coap-setup/deps/californium/deter/scripts/config.sh

node_type=$1

if [ $node_type = "proxy" ]; then
  sleep_amt=$PROXY_DURATION
  rm -f $TMP_DATA/$PROXY_TCPDUMP
  touch $TMP_DATA/$PROXY_TCPDUMP
  eval "tcpdump -i any port '($ORIGIN_SERVER_PORT or 5683)' -w $TMP_DATA/$PROXY_TCPDUMP &"

elif [ $node_type = "attacker" ]; then
  sleep_amt=$ATTACKER_DURATION
  rm -f $TMP_DATA/$ATTACKER_TCPDUMP
  touch $TMP_DATA/$ATTACKER_TCPDUMP
  tcpdump -i any udp port 5683 -w $TMP_DATA/$ATTACKER_TCPDUMP &

elif [ $node_type = "origin_server" ]; then
  sleep_amt=$ORIGIN_SERVER_DURATION
  rm -f $TMP_DATA/$ORIGIN_SERVER_TCPDUMP
  touch $TMP_DATA/$ORIGIN_SERVER_TCPDUMP
  tcpdump -i any port $ORIGIN_SERVER_PORT -w $TMP_DATA/$ORIGIN_SERVER_TCPDUMP &

else
  echo "Unknown parameter"
  exit 1
fi

tcpdump_pid=$!

sleep $sleep_amt

kill $tcpdump_pid
