#!/bin/bash

source /proj/MIT-DoS/exp/coap-setup/deps/californium/deter/scripts/config.sh

# Make sure there are no java procs running
while [[ ! -z `pgrep java` ]]; do
  next_pid=`pgrep java | tail -1`
  echo "Killing $next_pid..."
  sudo kill -9 $next_pid
  echo "Done"
done

rm -f $TMP_DATA/$PROXY_LOGNAME
rm -f $TMP_DATA/$FLAMEGRAPH_NAME
touch $TMP_DATA/$PROXY_LOGNAME

proxy_logging="nothanks"
pid_error_file="$TMP_DATA/java_error%p.log"
proxy_args="-Xmx${PROXY_HEAP_SIZE_MB}m"

if [[ $DO_PROXY_LOGGING -eq 1 ]]; then
  # Include argument to do stdout logging in the proxy
  proxy_logging="log"
fi

if [[ $DO_JAVA_PROFILING -eq 1 ]]; then
  # Set kernel parameters to enable perf profiling
  sudo sysctl -w kernel.perf_event_paranoid=1
  sudo sysctl -w kernel.kptr_restrict=0
fi

# Run the proxy with stderr and stdout redirected to proxy log
eval "pwd"
echo "Running proxy..."
((sudo java $proxy_args -jar $CF_HOME/demo-apps/run/cf-proxy2-3.0.0-SNAPSHOT.jar BasicForwardingProxy2 $proxy_logging $PROXY_CONNECTIONS) > $TMP_DATA/$PROXY_LOGNAME 2>&1) &

# Wait until proxy pid shows up
while [[ -z `pgrep java` ]]; do
  sleep 0.1
done

eval "ps aux | grep java"

echo "Found pids `pgrep java`"
proxy_pid=`pgrep java`
echo "Ran proxy with pid $proxy_pid..."

# Start profiler
if [[ $DO_JAVA_PROFILING -eq 1 ]]; then
  cd $UTILS_HOME/$PROFILER_DIR_NAME
  echo "Starting profiling..."
  sudo ./profiler.sh start -t -e $PROFILING_EVENT $proxy_pid
  echo "Done"
fi

echo "Sleeping for $PROXY_DURATION seconds..."
sleep $PROXY_DURATION
echo "Woke up"

if [[ $DO_JAVA_PROFILING -eq 1 ]]; then
  # Create and prepare the flamegraph svg
  sudo touch $TMP_DATA/$FLAMEGRAPH_NAME
  sudo chmod 666 $TMP_DATA/$FLAMEGRAPH_NAME

  # Stop profiling and dump output
  cd $UTILS_HOME/$PROFILER_DIR_NAME
  echo "Stopping profiling..."
  sudo ./profiler.sh stop -f $TMP_DATA/$FLAMEGRAPH_NAME --width 1500 --title $PROFILING_EVENT $proxy_pid
  echo "Done"
fi

# Kill proxy
echo "Killing $proxy_pid..."
sudo kill $proxy_pid
sudo kill -9 $proxy_pid
echo "Done"

# Kill all other java procs
while [[ ! -z `pgrep java` ]]; do
  next_pid=`pgrep java | tail -1`
  echo "Killing $next_pid..."
  sudo kill -9 $next_pid
  echo "Done"
done
