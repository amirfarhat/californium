
. /proj/MIT-DoS/exp/coap-setup/deps/californium/deter/scripts/config.sh

rm -f $TMP_DATA/$PROXY_LOGNAME
touch $TMP_DATA/$PROXY_LOGNAME

java -jar $CF_HOME/demo-apps/run/cf-proxy2-3.0.0-SNAPSHOT.jar BasicForwardingProxy2 > $TMP_DATA/$PROXY_LOGNAME

proxy_pid=$!

sleep $PROXY_DURATION

kill $proxy_pid
