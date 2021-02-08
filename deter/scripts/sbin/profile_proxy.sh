#!/bin/bash

source /proj/MIT-DoS/exp/coap-setup/deps/californium/deter/scripts/config.sh

proxy_pid=`pidof java`

# Create and prepare the flamegraph svg
sudo touch $TMP_DATA/$FLAMEGRAPH_NAME
sudo chmod 666 $TMP_DATA/$FLAMEGRAPH_NAME

# Launch profiler
cd $UTILS_HOME/$PROFILER_DIR_NAME
sudo bash profiler.sh -d $PROXY_DURATION -f $TMP_DATA/$FLAMEGRAPH_NAME $proxy_pid