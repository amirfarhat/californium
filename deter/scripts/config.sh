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

# Home directories
DETER_HOME=$CF_HOME/deter
SCRIPTS_HOME=$DETER_HOME/scripts
BIN_HOME=$SCRIPTS_HOME/sbin
UTILS_HOME=$DETER_HOME/utils
TMP=/tmp
TMP_DATA=/tmp/data

RUN_USER="amirf"

PAUSE_TIME=5 # Pause time after launching infra
WAIT_TIME=10 # Wait time after experiment finishes

# Binary toggles
TCPDUMP=1
ORIGIN_SERVER_APACHE=1
DO_PROXY_LOGGING=0
PROXY_TOP=1
DO_JAVA_PROFILING=1
RUN_ATTACKER=1
RUN_CLIENT=1

# Tunable parameters
TOP_INTERVAL=1
PROXY_CONNECTIONS=100
NUM_CLIENT_MESSAGES=500000
PROFILING_EVENT="alloc"

# Tunable durations
ORIGIN_SERVER_DURATION=150
ATTACKER_DURATION=$(( $ORIGIN_SERVER_DURATION / 5 ))
RECEIVER_DURATION=$(( $ORIGIN_SERVER_DURATION + $PAUSE_TIME ))
PROXY_DURATION=$ORIGIN_SERVER_DURATION
CLIENT_DURATION=$(( $ORIGIN_SERVER_DURATION - $PAUSE_TIME ))

# Java Perf Profiling
FLAMEGRAPH_NAME="flamegraph.svg"
PROFILER_DIR_NAME="async-profiler-1.8.3-linux-x64"
PROFILE_BINARY_NAME="$PROFILER_DIR_NAME.tar.gz"
PROFILE_BINARY_URL="https://github.com/jvm-profiling-tools/async-profiler/releases/download/v1.8.3/$PROFILE_BINARY_NAME"

# Origin server
ORIGIN_SERVER_NAME="originserver.coap-setup.MIT-DoS.isi.deterlab.net"
ORIGIN_SERVER_TCPDUMP="server_dump.pcap"
ORIGIN_SERVER_PERF="server_perf.data"
ORIGIN_SERVER_ACCESS_LOGNAME="server_access.log"
ORIGIN_SERVER_ERROR_LOGNAME="server_error.log"
ORIGIN_SERVER_PORT=80

# Receiver
RECEIVER_NAME="receiver.coap-setup.MIT-DoS.isi.deterlab.net"
RECEIVER_TCPDUMP="receiver_dump.pcap"
RECEIVER_COAP_PORT="5683"

# Attacker
ATTACKER_NAME="attacker.coap-setup.MIT-DoS.isi.deterlab.net"
ATTACKER_TCPDUMP="attacker_dump.pcap"
ATTACKER_PERF="attacker_perf.data"
ATTACKER_LOGNAME="attacker.log"
ATTACKER_SPOOFED_PORT=$RECEIVER_COAP_PORT

# Proxy
PROXY_NAME="proxy.coap-setup.MIT-DoS.isi.deterlab.net"
PROXY_TCPDUMP="proxy_dump.pcap"
PROXY_PERF="proxy_perf.data"
PROXY_LOGNAME="proxy.log"
PROXY_TOPNAME="proxy.top"
PROXY_COAP_PORT="5683"

# Client
CLIENT_NAME="client.coap-setup.MIT-DoS.isi.deterlab.net"
CLIENT_TCPDUMP="client_dump.pcap"
CLIENT_LOGNAME="client.log"

# Collection of all hosts
HOST_NAMES=(
  "$ATTACKER_NAME"
  "$ORIGIN_SERVER_NAME"
  "$PROXY_NAME"
  "$RECEIVER_NAME"
  "$CLIENT_NAME"
)
