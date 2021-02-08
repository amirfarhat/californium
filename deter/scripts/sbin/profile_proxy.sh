#!/bin/bash

source /proj/MIT-DoS/exp/coap-setup/deps/californium/deter/scripts/config.sh

# Get PID of the already running proxy
proxy_pid=`pidof java`
echo "PROFILING PROXY PID $proxy_pid"

# Set kernel parameters to enable perf profiling
sudo sysctl -w kernel.perf_event_paranoid=1
sudo sysctl -w kernel.kptr_restrict=0

# Create and prepare the flamegraph svg
sudo touch $TMP_DATA/$FLAMEGRAPH_NAME
sudo chmod 666 $TMP_DATA/$FLAMEGRAPH_NAME

# Launch profiler
cd $UTILS_HOME/$PROFILER_DIR_NAME
./profiler.sh -d $PROXY_DURATION -f $TMP_DATA/$FLAMEGRAPH_NAME $proxy_pid
