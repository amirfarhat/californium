
. /proj/MIT-DoS/exp/coap-setup/deps/californium/deter/scripts/config.sh

rm -f $TMP_DATA/$ORIGIN_SERVER_LOGNAME
touch $TMP_DATA/$ORIGIN_SERVER_LOGNAME

python3 $DETER_HOME/multislowserver.py -p 8000 -d 1 -x True > $TMP_DATA/$ORIGIN_SERVER_LOGNAME 2>&1

server_pid=$!

sleep $ORIGIN_SERVER_DURATION

kill $server_pid
