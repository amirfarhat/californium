import csv
import argparse

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
LogEntry = recordclass('LogEntry', 'yes_responses no_responses')

with open(args.http_log, 'r') as f:
  L = f.readline()
  while L:
    if L.startswith("===================="):
      parts = L.split()
      window = int(parts[1])
      records[window] = LogEntry(\
        yes_responses = 0,
        no_responses  = 0,
      )
    else:
      if L.startswith("Y"):
        records[window].yes_responses += 1
      elif L.startswith("N"):
        records[window].no_responses += 1
    L = f.readline()

windows = []
failure_percentages = []
for w, r in records.items():
  fail_pct = 100 * r.no_responses / (r.no_responses + r.yes_responses)
  print(f"{w}: {fail_pct} failed")

  windows.append(w)
  failure_percentages.append(fail_pct)

if args.graph:
  plt.plot(windows, failure_percentages, 'b')
  plt.title("HTTP Request Failure Rate vs Outstanding Requests")
  plt.xlabel("# Outstanding HTTP Requests")
  plt.ylabel("Percent of Failed Responses")
  plt.show()