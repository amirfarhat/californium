#!/bin/bash

source /proj/MIT-DoS/exp/coap-setup/deps/californium/deter/scripts/config.sh

PROXY_IP=`bash $DETER_HOME/fetchips.sh proxy`
ORIGIN_SERVER_IP=`bash $DETER_HOME/fetchips.sh proxy originserver`

# Make sure there are no java procs running
while [[ ! -z `pgrep java` ]]; do
  next_pid=`pgrep java | tail -1`
  echo "Killing $next_pid..."
  sudo kill -9 $next_pid
  echo "Done"
done

sudo rm -f $TMP_DATA/$CLIENT_LOGNAME
sudo touch $TMP_DATA/$CLIENT_LOGNAME

proxy_uri="coap://$PROXY_IP:$PROXY_COAP_PORT/coap2http"
destination_uri="http://$ORIGIN_SERVER_IP:$ORIGIN_SERVER_PORT"

echo "Running client..."
((sudo java -jar $CF_HOME/demo-apps/run/cf-proxy2-3.0.0-SNAPSHOT.jar ExampleProxy2CoapClient "$proxy_uri" "$destination_uri" "$NUM_CLIENT_MESSAGES") > $TMP_DATA/$CLIENT_LOGNAME 2>&1) &

# Wait until client pid shows up
while [[ -z `pgrep java` ]]; do
  sleep 0.1
done
client_pid=`pgrep java`
echo "Ran client with pid $client_pid..."

echo "Sleeping for $CLIENT_DURATION seconds..."
sleep $CLIENT_DURATION
echo "Woke up"

# Kill client
echo "Killing $client_pid..."
sudo kill -9 $client_pid
echo "Done"

# Kill all other java procs
while [[ ! -z `pgrep java` ]]; do
  next_pid=`pgrep java | tail -1`
  echo "Killing $next_pid..."
  sudo kill -9 $next_pid
  echo "Done"
done