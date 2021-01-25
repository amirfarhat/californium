import datetime
import argparse

import numpy as np
from icecream import ic
import matplotlib.pyplot as plt
from recordclass import recordclass
from collections import OrderedDict

def parse_args():
  parser = argparse.ArgumentParser(description = 'Plot proxy req/res timing data')
  parser.add_argument('-p', '--proxy-log', dest='proxy_log',
                      help='Proxy operation log', action='store',
                      default="pxy_waterfall_same_host", type=str)
  return parser.parse_args()

args = parse_args()

ProxyRecord = recordclass('ProxyRecord', 'coap_recv coap_translate http_recv http_translate http_fail ')
min_timestamp = float('inf')
data = OrderedDict()

with open(args.proxy_log, 'r') as f:
  L = f.readline()
  while L:
    # Line must be a custom debugging statement
    dbg = L.replace("[DBG] ", "")
    if len(dbg) < len(L):

      # Parse log line. Example format:
      # [DBG] 842877217958983 COAP_RECEIVED 44167_45FD2841
      parts = dbg.split()
      timestamp_ns = int(parts[0])
      event = parts[1]
      request_handle = parts[2]

      min_timestamp = min(min_timestamp, timestamp_ns)

      if event == "COAP_RECEIVED":
        data[request_handle] = ProxyRecord(\
          coap_recv=timestamp_ns,
          coap_translate=None,
          http_recv=None,
          http_translate=None,
          http_fail=True,
        )
        
      elif event == "COAP_TRANSLATED":
        data[request_handle].coap_translate = timestamp_ns

      elif event == "HTTP_RECVD_SUCCESS":
        data[request_handle].http_recv = timestamp_ns
        data[request_handle].http_fail = False

      elif event == "HTTP_TRANSLATED":
        data[request_handle].http_translate = timestamp_ns

      elif event == "HTTP_RECVD_FAILED":
        data[request_handle].http_recv = timestamp_ns

      elif event == "HTTP_RECVD_CANCELLED":
        data[request_handle].http_recv = timestamp_ns

      else:
        raise Exception(f"Got {L}")

    L = f.readline()

all_message_numbers = []
message_numbers = []
coap_translation_times = []
request_return_times = []
http_translation_times = []
failed = 0

for i, (request_handle, r) in enumerate(data.items()):
  message_number = i + 1
  all_message_numbers.append(message_number)
  if r.http_translate:
    message_numbers.append(message_number)

    coap_translation_time = r.coap_translate - r.coap_recv
    coap_translation_times.append(coap_translation_time)

    request_return_time = r.http_recv - r.coap_translate
    request_return_time *= 1e-9
    request_return_times.append(request_return_time)

    
    http_translation_time = r.http_translate - r.http_recv
    http_translation_times.append(http_translation_time)
  else:
    failed += 1

print(f"avg coap_translation_times = {np.average(coap_translation_times)}")
print(f"avg request_return_times = {np.average(request_return_times)}")
print(f"avg http_translation_times = {np.average(http_translation_times)}")
print(f"failed proxy->server requests = {failed}/{len(all_message_numbers)}")

# fig, ax = plt.subplots(2)

# ax[0].bar(message_numbers, coap_translation_times, label="CoAP->HTTP Translation")
# ax[0].bar(message_numbers, http_translation_times, label="HTTP-> Translation")
# ax[0].set_title("Protocol Translation Duration Per Message")
# ax[0].set_xlabel("Message Number")
# ax[0].set_ylabel("Time Duration [nanosecond]")
# ax[0].legend()

# ax[1].bar(message_numbers, request_return_times, label="Proxy->Server RTT")
# ax[1].set_title("Message RTT from Proxy to Server")
# ax[1].set_xlabel("Message Number")
# ax[1].set_ylabel("Time Duration [second]")
# ax[1].legend()

# plt.show()