#!/bin/bash

source ./config.sh

rm -f $TMP_DATA/$ATTACKER_TCPDUMP

sudo tcpdump -i any udp port 5683 -w $TMP_DATA/$ATTACKER_TCPDUMP &
tcpdump_pid=$!

sleep $ATTACKER_DURATION

sudo kill $tcpdump_pid