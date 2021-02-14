#!/bin/bash

# Write experiment link info
fname="exp_links_info.txt"
expinfo -l -e MIT-DoS,coap-setup > $fname

# Populate distributed map of IPs
mkdir -p ips
python storeips_helper.py
