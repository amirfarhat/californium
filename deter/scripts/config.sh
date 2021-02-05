#!/bin/bash

host_name=$(hostname | awk '{print tolower($0)}')

# Determine where home is based on host
if [[ $host_name == *"deter"* ]]; then
  CF_HOME=/proj/MIT-DoS/exp/coap-setup/deps/californium
elif [[ $host_name == *"amir"* ]]; then
  CF_HOME=/Users/amirfarhat/workplace/research/californium
else
  CF_HOME=~/californium
fi

DETER_HOME=$CF_HOME/deter
SCRIPTS_HOME=$DETER_HOME/scripts
BIN_HOME=$SCRIPTS_HOME/sbin

# Tcpdump
TCPDUMP=1
TCPDUMP_BUFFER_KIBS=2000000

# HTTP Server
ORIGIN_SERVER_APACHE=1

# Top
PROXY_TOP=1
TOP_INTERVAL=1

# Logging
DO_PROXY_LOGGING=1

# Sysctl
NETDEV_MAX_BACKLOG=500000

TMP=/tmp
TMP_DATA=/tmp/data

ATTACKER_NAME="attacker.coap-setup.MIT-DoS.isi.deterlab.net"
ATTACKER_TCPDUMP="attacker_dump.pcap"
ATTACKER_LOGNAME="attacker.log"
ATTACKER_IP="10.1.1.2"
ATTACKER_SPOOFED_IP="8.8.8.8"
ATTACKER_SPOOFED_PORT="7123"
ATTACKER_DURATION=20

ORIGIN_SERVER_NAME="originserver.coap-setup.MIT-DoS.isi.deterlab.net"
ORIGIN_SERVER_TCPDUMP="server_dump.pcap"
ORIGIN_SERVER_LOGNAME="server.log"
ORIGIN_SERVER_IP="10.1.2.3"
ORIGIN_SERVER_PORT=80
ORIGIN_SERVER_DURATION=120

PROXY_NAME="proxy.coap-setup.MIT-DoS.isi.deterlab.net"
PROXY_TCPDUMP="proxy_dump.pcap"
PROXY_LOGNAME="proxy.log"
PROXY_TOPNAME="proxy.top"
PROXY_IP="10.1.1.3"
PROXY_COAP_PORT="5683"
PROXY_DURATION=$ORIGIN_SERVER_DURATION

RUN_USER="amirf"

HOST_NAMES=(
  "$ATTACKER_NAME"
  "$ORIGIN_SERVER_NAME"
  "$PROXY_NAME"
)