#!/bin/bash

source /proj/MIT-DoS/exp/coap-setup/deps/californium/deter/scripts/config.sh

cd $DETER_HOME

# Write experiment link info
fname="exp_links_info.txt"
rm $fname
expinfo -l -e MIT-DoS,coap-setup > $fname

# Populate distributed map of IPs
rm -r ips/
mkdir -p ips
python storeips_helper.py