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

  # Create and prepare the flamegraph svg
  sudo touch $TMP_DATA/$FLAMEGRAPH_NAME
  sudo chmod 666 $TMP_DATA/$FLAMEGRAPH_NAME

  agentpath="-agentpath:$UTILS_HOME/$PROFILER_DIR_NAME/build/libasyncProfiler.so=start,file=$TMP_DATA/$FLAMEGRAPH_NAME"
fi

# Run the proxy
((sudo java $agentpath $jvm_args -jar $CF_HOME/demo-apps/run/cf-proxy2-3.0.0-SNAPSHOT.jar BasicForwardingProxy2 $proxy_args) > $TMP_DATA/$PROXY_LOGNAME) &

proxy_pid=`pidof java`

sleep $PROXY_DURATION

kill $proxy_pid