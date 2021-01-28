#!/bin/bash

. /proj/MIT-DoS/exp/coap-setup/deps/californium/deter/scripts/config.sh

rm -f $TMP_DATA/$PROXY_TCPDUMP
touch $TMP_DATA/$PROXY_TCPDUMP

tcpdump -i any port '(8000 or 5683)' $TMP_DATA/$PROXY_TCPDUMP &
tcpdump_pid=$!

sleep $PROXY_DURATION

kill $tcpdump_pid
