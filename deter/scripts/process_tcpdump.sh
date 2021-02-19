#!/bin/bash

# Parse inputs
me=`basename "$0"`
input_file=$1
output_file=$2
if [[ -z "$input_file" ]] || [[ -z "$output_file" ]]; then
  echo "$me: Usage [input_file] [output_file]"
  exit 1
fi

filter="coap || http"

# Run tshark in the backend to handle parsing and 
# high-level protocol filtering
(tshark \
  -r "$input_file" \
  -2 \
  -n \
  -R "$filter" \
  -t e) > "$output_file"