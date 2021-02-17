#!/bin/bash

source /proj/MIT-DoS/exp/coap-setup/deps/californium/deter/scripts/config.sh

rm -f $TMP_DATA/$ORIGIN_SERVER_ACCESS_LOGNAME
touch $TMP_DATA/$ORIGIN_SERVER_ACCESS_LOGNAME

rm -f $TMP_DATA/$ORIGIN_SERVER_ERROR_LOGNAME
touch $TMP_DATA/$ORIGIN_SERVER_ERROR_LOGNAME

if [[ $ORIGIN_SERVER_APACHE -eq 1 ]]; then
  # Start server async, sleep, then kill
  sudo /etc/init.d/apache2 start
  sudo /etc/init.d/apache2 restart
  sleep $ORIGIN_SERVER_DURATION
  sudo /etc/init.d/apache2 stop
  
  # Copy server access log
  sudo cp /var/log/apache2/access.log $TMP_DATA/$ORIGIN_SERVER_ACCESS_LOGNAME
  sudo rm /var/log/apache2/access.log

  # Copy server error log
  sudo cp /var/log/apache2/error.log $TMP_DATA/$ORIGIN_SERVER_ERROR_LOGNAME
  sudo rm /var/log/apache2/error.log

else
  (python3 $DETER_HOME/multislowserver.py -p $ORIGIN_SERVER_PORT -d 1 -x True > $TMP_DATA/$ORIGIN_SERVER_LOGNAME 2>&1) &
  server_pid=$!
  sleep $ORIGIN_SERVER_DURATION
  kill $server_pid
fi
