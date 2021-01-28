
. /proj/MIT-DoS/exp/coap-setup/deps/californium/deter/scripts/config.sh

rm -f $TMP_DATA/$ATTACKER_TCPDUMP
touch $TMP_DATA/$ATTACKER_TCPDUMP

tcpdump -i any udp port 5683 -w $TMP_DATA/$ATTACKER_TCPDUMP &
tcpdump_pid=$!

sleep $ATTACKER_DURATION

kill $tcpdump_pid
