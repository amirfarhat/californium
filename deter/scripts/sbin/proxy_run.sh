#!/bin/bash

source /proj/MIT-DoS/exp/coap-setup/deps/californium/deter/scripts/config.sh

rm -f $TMP_DATA/$PROXY_LOGNAME
rm -f $TMP_DATA/$FLAMEGRAPH_NAME
touch $TMP_DATA/$PROXY_LOGNAME

proxy_args=""
agentpath=""

if [[ $DO_PROXY_LOGGING -eq 1 ]]; then
  # Include argument to do stdout logging in the proxy
  proxy_args="log"
fi

if [[ $DO_JAVA_PROFILING -eq 1 ]]; then
  # Set kernel parameters to enable perf profiling
  sudo sysctl -w kernel.perf_event_paranoid=1
  sudo sysctl -w kernel.kptr_restrict=0

  # Specify agent for CPU profiling 
  agent="-agentpath:$UTILS_HOME/$PROFILER_DIR_NAME/build/libasyncProfiler.so=start,event=cpu"
fi

# Run the proxy with stderr and stdout redirected to proxy log
((sudo java $agent $jvm_args -jar $CF_HOME/demo-apps/run/cf-proxy2-3.0.0-SNAPSHOT.jar BasicForwardingProxy2 $proxy_args) > $TMP_DATA/$PROXY_LOGNAME 2>&1) &
proxy_pid=`pgrep java`

sleep $PROXY_DURATION

if [[ $DO_PROXY_LOGGING -eq 1 ]]; then
  # Create and prepare the flamegraph svg
  sudo touch $TMP_DATA/$FLAMEGRAPH_NAME
  sudo chmod 666 $TMP_DATA/$FLAMEGRAPH_NAME

  # Stop profiling and dump output
  cd $UTILS_HOME/$PROFILER_DIR_NAME
  sudo ./profiler.sh stop -f $TMP_DATA/$FLAMEGRAPH_NAME --width 1600 $proxy_pid
fi

sudo kill -9 $proxy_pid