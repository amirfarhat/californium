proxy_ip=$1

origin_ip=$2

my_ip=$3
if [ -z $my_ip ]
then
	my_ip=`hostname -I | awk '{ printf $1 }'`
fi

me=`basename "$0"`

control_c() {
  echo "$me KILLED"
}

trap control_c SIGINT

sudo python3 coapspoofer.py \
  --debug \
  --source $my_ip \
  --src-port 7123 \
  --destination $proxy_ip \
  --dst-port 5683 \
  --message-type CON \
  --code 001 \
  --uri-host $proxy_ip \
  --uri-path coap2http \
  --proxy-uri http://$origin_ip:8000 \
  --num-messages 10 &
sleep 5
p=$!
kill $p