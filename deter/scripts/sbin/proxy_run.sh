#!/bin/bash

source /proj/MIT-DoS/exp/coap-setup/deps/californium/deter/scripts/config.sh

rm -f $TMP_DATA/$PROXY_LOGNAME
touch $TMP_DATA/$PROXY_LOGNAME

proxy_args=""
jvm_args=""

# Include argument to do stdout logging in the proxy
if [[ $DO_PROXY_LOGGING -eq 1 ]]; then
  proxy_args="log"
fi

# Set up Java profiling
if [[ $DO_JAVA_PROFILING -eq 1 ]]; then
  # Set kernel parameters to enable perf profiling
  sudo sysctl -w kernel.perf_event_paranoid=1
  sudo sysctl -w kernel.kptr_restrict=0

  # Include frame pointer for Java profiling
  jvm_args="-XX:+UnlockDiagnosticVMOptions -XX:+DebugNonSafepoints"
fi

# Run the proxy
((java $jvm_args -jar $CF_HOME/demo-apps/run/cf-proxy2-3.0.0-SNAPSHOT.jar BasicForwardingProxy2 $proxy_args) > $TMP_DATA/$PROXY_LOGNAME) &

proxy_pid=`pidof java`

sleep $PROXY_DURATION

kill $proxy_pid
kill -9 `pidof java`
