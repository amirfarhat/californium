#!/bin/bash

# TODO: See mergecap
# https://www.wireshark.org/docs/wsug_html_chunked/ChIOMergeSection.html

# Run wireshark CLI to get CoAP message summary
tshark \
  -r $1 \
  -2 \
  -n \
  -R "(coap) && (coap.type == 0)" \
  -t ad > $2