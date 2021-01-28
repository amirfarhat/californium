
CF_HOME=/proj/MIT-DoS/exp/coap-setup/deps/californium
DETER_HOME=$CF_HOME/deter
SCRIPTS_HOME=$DETER_HOME/scripts
BIN_HOME=$SCRIPTS_HOME/sbin

TCPDUMP=1

TMP=/tmp
TMP_DATA=/tmp/data

ATTACKER_NAME="attacker.coap-setup.MIT-DoS.isi.deterlab.net"
ATTACKER_TCPDUMP="attacker_dump.pcap"
ATTACKER_LOGNAME="attacker.log"
ATTACKER_IP="10.1.1.2"
ATTACKER_DURATION=10

ORIGIN_SERVER_NAME="originserver.coap-setup.MIT-DoS.isi.deterlab.net"
ORIGIN_SERVER_TCPDUMP="server_dump.pcap"
ORIGIN_SERVER_LOGNAME="server.log"
ORIGIN_SERVER_IP="10.1.2.3"
ORIGIN_SERVER_DURATION=90

PROXY_NAME="proxy.coap-setup.MIT-DoS.isi.deterlab.net"
PROXY_TCPDUMP="proxy_dump.pcap"
PROXY_LOGNAME="proxy.log"
PROXY_IP="10.1.1.3"
PROXY_DURATION=90

RUN_USER="amirf"

HOST_NAMES=(
  "$ATTACKER_NAME"
  "$ORIGIN_SERVER_NAME"
  "$PROXY_NAME"
)