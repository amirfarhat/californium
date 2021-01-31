import csv
import argparse

import numpy as np
import matplotlib.pyplot as plt

from icecream import ic
from collections import OrderedDict
from recordclass import recordclass

def parse_args():
  parser = argparse.ArgumentParser(description = '')
  parser.add_argument('-l', '--http-log', dest='http_log',
                      help='Log of async http client', action='store', type=str)
  parser.add_argument('-g', '--graph', dest='graph', action='store_true')
  return parser.parse_args()

args = parse_args()

records = OrderedDict()
LogEntry = recordclass('LogEntry', 'yes_responses no_responses request_times response_times')

with open(args.http_log, 'r') as f:
  L = f.readline()
  while L:
    parts = L.split()
    if L.startswith("==="):
      window = int(parts[1])
      records[window] = LogEntry(\
        yes_responses = 0,
        no_responses  = 0,
        request_times = [ 0 for _ in range(window) ],
        response_times = [ 0 for _ in range(window) ],
      )
    else:
      if L.startswith("REQ"):
        msg = int(parts[1])
        timestamp_ns = int(parts[2])
        records[window].request_times[msg] = timestamp_ns

      elif L.startswith("Y"):
        msg = int(parts[2])
        timestamp_ns = int(parts[3])
        records[window].yes_responses += 1
        records[window].response_times[msg] = timestamp_ns

      elif L.startswith("N"):
        records[window].no_responses += 1

    L = f.readline()

msg_id = 1
msg_ids = []
msg_response_times_sec = np.zeros(sum(records.keys()))
windows = []
failure_percentages = []
for w, r in records.items():
  fail_pct = 100 * r.no_responses / (r.no_responses + r.yes_responses)
  print(f"{w}: {fail_pct} failed")

  for qtime, ptime in zip(r.request_times, r.response_times):
    msg_ids.append(msg_id)
    response_time_sec = max(-1, (ptime - qtime) * 1e-9)
    msg_response_times_sec[msg_id-1] = response_time_sec
    msg_id += 1

  windows.append(w)
  failure_percentages.append(fail_pct)

if args.graph:
  fig, ax = plt.subplots(2)

  ax[0].plot(windows, failure_percentages, 'b')
  ax[0].set_title("HTTP Request Failure Rate vs Outstanding Requests")
  ax[0].set_xlabel("# Outstanding HTTP Requests")
  ax[0].set_ylabel("Percent of Failed Responses")
  ax[0].set_xscale("log", base=2)

  good_msgs = np.ma.masked_where(msg_response_times_sec >= 0, msg_response_times_sec)
  bad_msgs = np.ma.masked_where(msg_response_times_sec < 0, msg_response_times_sec)
  ax[1].plot(msg_ids, good_msgs, bad_msgs, 'r')
  ax[1].set_title("Message Response Times")
  ax[1].set_xlabel("Message ID")
  ax[1].set_ylabel("Response Time [second]")
  # ax[1].set_xscale("log", base=2)

  plt.show()