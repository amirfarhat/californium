#!/bin/bash

# Attacker TcpDump
# Proxy TcpDump
# Proxy CoAP->HTTP Translation
# Proxy<->Server Trip
# Proxy HTTP->CoAP Translation

# Make sure all processed dumps exit before analysis
for D in $1/*; do
  if [[ ! -f $D/processed_attacker_dump.out ]]; then
    echo "Processing attacker dump in $D"
    ./process_tcpdump.sh $D/attacker_dump.pcap $D/processed_attacker_dump.out
  fi
  if [[ ! -f $D/processed_proxy_dump.out ]]; then
    echo "Processing proxy dump in $D"
    ./process_tcpdump.sh $D/proxy_dump.pcap $D/processed_proxy_dump.out
  fi
done

# Execute analysis of all trials
for D in $1/*; do
  echo "Trial $D"
  python3 /Users/amirfarhat/workplace/research/californium/deter/scripts/plot_tcpdump.py -a $D/processed_attacker_dump.out -p $D/processed_proxy_dump.out -l $D/proxy.log
done