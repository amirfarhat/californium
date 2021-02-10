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
UTILS_HOME=$DETER_HOME/utils

RUN_USER="amirf"

# Pause time between stages
PAUSE_TIME=5
WAIT_TIME=20

# Tcpdump
TCPDUMP=1

# HTTP Server
ORIGIN_SERVER_APACHE=1

# Top
PROXY_TOP=1
TOP_INTERVAL=1

# Java Perf Profiling
DO_JAVA_PROFILING=1
FLAMEGRAPH_NAME="flamegraph.svg"
PROFILER_DIR_NAME="async-profiler-1.8.3-linux-x64"
PROFILE_BINARY_NAME="$PROFILER_DIR_NAME.tar.gz"
PROFILE_BINARY_URL="https://github.com/jvm-profiling-tools/async-profiler/releases/download/v1.8.3/$PROFILE_BINARY_NAME"

# Logging
DO_PROXY_LOGGING=1

TMP=/tmp
TMP_DATA=/tmp/data

ORIGIN_SERVER_NAME="originserver.coap-setup.MIT-DoS.isi.deterlab.net"
ORIGIN_SERVER_TCPDUMP="server_dump.pcap"
ORIGIN_SERVER_PERF="server_perf.data"
ORIGIN_SERVER_LOGNAME="server.log"
ORIGIN_SERVER_IP="10.1.3.3"
ORIGIN_SERVER_PORT=80
ORIGIN_SERVER_DURATION=120

RECEIVER_NAME="receiver.coap-setup.MIT-DoS.isi.deterlab.net"
RECEIVER_TCPDUMP="receiver_dump.pcap"
RECEIVER_IP="10.1.1.3"
RECEIVER_COAP_PORT="5683"
RECEIVER_DURATION=$ORIGIN_SERVER_DURATION

ATTACKER_NAME="attacker.coap-setup.MIT-DoS.isi.deterlab.net"
ATTACKER_TCPDUMP="attacker_dump.pcap"
ATTACKER_PERF="attacker_perf.data"
ATTACKER_LOGNAME="attacker.log"
ATTACKER_IP="10.1.1.3"
ATTACKER_SPOOFED_IP=$RECEIVER_IP
ATTACKER_SPOOFED_PORT=$RECEIVER_COAP_PORT
ATTACKER_DURATION=20

PROXY_NAME="proxy.coap-setup.MIT-DoS.isi.deterlab.net"
PROXY_TCPDUMP="proxy_dump.pcap"
PROXY_PERF="proxy_perf.data"
PROXY_LOGNAME="proxy.log"
PROXY_TOPNAME="proxy.top"
PROXY_IP="10.1.2.3"
PROXY_COAP_PORT="5683"
PROXY_DURATION=$ORIGIN_SERVER_DURATION

HOST_NAMES=(
  "$ATTACKER_NAME"
  "$ORIGIN_SERVER_NAME"
  "$PROXY_NAME"
  "$RECEIVER_NAME"
)