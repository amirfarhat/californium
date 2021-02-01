#!/bin/bash

source /proj/MIT-DoS/exp/coap-setup/deps/californium/deter/scripts/config.sh

rm -f $TMP_DATA/$PROXY_TOPNAME

timeout $PROXY_DURATION top -b -d $TOP_INTERVAL > $TMP_DATA/$PROXY_TOPNAME

