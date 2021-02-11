#!/bin/bash

# TODO: See mergecap
# https://www.wireshark.org/docs/wsug_html_chunked/ChIOMergeSection.html

input_file=$1

output_file=$2

node_type=$3
if [[ $node_type == "receiver" ]]; then
  filter="coap"
else
  filter="coap && coap.type == 0"
fi
echo $filter

# Run wireshark CLI to get CoAP message summary
tshark \
  -r $input_file \
  -2 \
  -n \
  -R "$filter" \
  -t e > $output_file