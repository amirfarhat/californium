sudo python3 coapspoofer.py \
  --debug \
  --source 127.0.0.1 \
  --src-port 7123 \
  --destination 127.0.0.1 \
  --dst-port 5683 \
  --message-type CON \
  --code 001 \
  --uri-host 127.0.0.1 \
  --uri-path coap2http \
  --proxy-uri http://127.0.0.1:8000 \
  --num-messages 750 \