import os
import datetime
import argparse

import numpy as np
from icecream import ic
import matplotlib.pyplot as plt
from recordclass import recordclass
from collections import OrderedDict

def parse_args():
  parser = argparse.ArgumentParser(description = '')
  parser.add_argument('-d', '--experiment-directory', dest='experiment_directory',
                      help='', action='store', type=str)
  parser.add_argument('-g', '--graph', dest='graph', action='store_true')
  return parser.parse_args()

args = parse_args()

ProxyRecord = recordclass('ProxyRecord', 'coap_recv coap_translate http_recv http_translate http_fail ')

def parse_proxy_file(proxy_file):
  min_timestamp = float('inf')
  data = OrderedDict()

  with open(proxy_file, 'r') as f:
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
  
  return data, min_timestamp

def populate_from_run(proxy_file):
  data, min_timestamp = parse_proxy_file(proxy_file)

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
      coap_translation_time *= 1e-6 
      coap_translation_times.append(coap_translation_time)

      request_return_time = r.http_recv - r.coap_translate
      request_return_time *= 1e-9
      request_return_times.append(request_return_time)

      
      http_translation_time = r.http_translate - r.http_recv
      http_translation_time *= 1e-6
      http_translation_times.append(http_translation_time)
    else:
      failed += 1

  return all_message_numbers, message_numbers, coap_translation_times, request_return_times, http_translation_times, failed

if args.graph:
  fig, ax = plt.subplots(2, 2)

for run_dir_name in sorted(os.listdir(args.experiment_directory)):
  # Get run number
  if not run_dir_name.isnumeric():
    continue
  run_number = int(run_dir_name)

  # Get proxy log  
  proxy_file = f"{args.experiment_directory}/{run_number}/proxy.log"

  all_message_numbers, message_numbers, coap_translation_times, request_return_times, http_translation_times, failed = populate_from_run(proxy_file)

  # print(f"avg coap_translation_times = {np.average(coap_translation_times)}")
  # print(f"avg request_return_times = {np.average(request_return_times)}")
  # print(f"avg http_translation_times = {np.average(http_translation_times)}")
  # print(f"failed proxy->server requests = {100 * failed / len(all_message_numbers)}% = {failed}/{len(all_message_numbers)}")
  pct_failed_requests = 100 * failed / len(all_message_numbers)

  if args.graph:
    label = f"CoAP->HTTP Translation - Run {run_number}"
    ax[0, 0].plot(message_numbers, coap_translation_times, label=label)
    ax[0, 0].set_title("CoAP->HTTP Protocol Translation Duration Per Message")
    ax[0, 0].set_ylabel("Time Duration [nanosecond]")
    ax[0, 0].legend()

    label = f"HTTP->CoAP Translation - Run {run_number}"
    ax[1, 0].plot(message_numbers, http_translation_times, label=label)
    ax[1, 0].set_title("HTTP->CoAP Protocol Translation Duration Per Message")
    ax[1, 0].set_ylabel("Time Duration [nanosecond]")
    ax[1, 0].legend()

    label = f"Proxy->Server RTT - Run {run_number}"
    ax[0, 1].plot(message_numbers, request_return_times, label=label)
    ax[0, 1].set_title("Message RTT from Proxy to Server")
    ax[0, 1].set_xlabel("Message Number")
    ax[0, 1].set_ylabel("Time Duration [second]")
    ax[0, 1].legend()

    label = f"Percent of Failed Requests - Run {run_number}"
    ax[1, 1].bar(run_number, pct_failed_requests, label=label)
    ax[1, 1].set_title("Percent of Failed Requests Per Trial Run")
    ax[1, 1].set_xlabel("Trial Number")
    ax[1, 1].set_ylabel("Percent of Failed Requests")

if args.graph:
  plt.show()