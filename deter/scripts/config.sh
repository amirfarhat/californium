#!/bin/bash

if [[ "$OSTYPE" == "darwin"* ]]; then
  # Mac OSX local
  CF_HOME=/Users/amirfarhat/workplace/research/californium
else
  CF_HOME=/proj/MIT-DoS/exp/coap-setup/deps/californium
fi
        

DETER_HOME=$CF_HOME/deter
SCRIPTS_HOME=$DETER_HOME/scripts
BIN_HOME=$SCRIPTS_HOME/bin

TCPDUMP=1

TMP=/tmp
TMP_DATA=/tmp/data

if [[ "$OSTYPE" == "darwin"* ]]; then
  ATTACKER_NAME="127.0.0.1"
else
  ATTACKER_NAME="attacker.coap-setup.MIT-DoS.isi.deterlab.net"
fi
ATTACKER_TCPDUMP="attacker_dump.pcap"
if [[ "$OSTYPE" == "darwin"* ]]; then
  ATTACKER_IP="127.0.0.1"
else
  ATTACKER_IP="10.1.1.2"
fi
ATTACKER_DURATION=10

if [[ "$OSTYPE" == "darwin"* ]]; then
  RUN_USER = "amirfarhat"
else
  RUN_USER = "amirf"
fi