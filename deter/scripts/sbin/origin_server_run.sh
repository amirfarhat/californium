#!/bin/bash

. /proj/MIT-DoS/exp/coap-setup/deps/californium/deter/scripts/config.sh

rm -f $TMP_DATA/$ORIGIN_SERVER_LOGNAME
touch $TMP_DATA/$ORIGIN_SERVER_LOGNAME

if [[ $ORIGIN_SERVER_APACHE -eq 1 ]]; then
  sudo /etc/init.d/apache2 start
  sleep $ORIGIN_SERVER_DURATION
  sudo /etc/init.d/apache2 stop

else
  (python3 $DETER_HOME/multislowserver.py -p $ORIGIN_SERVER_PORT -d 1 -x True > $TMP_DATA/$ORIGIN_SERVER_LOGNAME 2>&1) &
  server_pid=$!
  sleep $ORIGIN_SERVER_DURATION
  kill $server_pid
fi
