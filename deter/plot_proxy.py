import datetime
import argparse

from icecream import ic
import matplotlib.pyplot as plt
from collections import namedtuple

def parse_args():
  parser = argparse.ArgumentParser(description = 'Plot proxy req/res timing data')
  parser.add_argument('-p', '--proxy-log', dest='proxy_log',
                      help='Proxy operation log', action='store',
                      default="pxy_waterfall_same_host", type=str)
  return parser.parse_args()

args = parse_args()

ProxyRecord = namedtuple('ProxyRecord', 'timestamp type message_id')

min_timestamp = datetime.datetime.now().timestamp()
min_message_id = float('inf')
records = []

with open(args.proxy_log, 'r') as f:
  # Skip header: first two lines
  f.readline()
  f.readline()

  L = f.readline()
  while L:
    # Parse and remove extra logging
    parts = map(str.lower, L.split())
    parts = filter(('debug').__ne__, parts)
    parts = list(filter(('[proxyhttpclientresource]:').__ne__, parts))
    
    # Parse message type
    if parts[1] in ['req', 'res']:
      message_type = parts[1]
    else:
      # Some error
      L = f.readline()
      continue

    # Parse timestamp
    dt = datetime.datetime.strptime(f"2021 {parts[0]}", "%Y %H:%M:%S.%f")
    timestamp = dt.timestamp()

    # Parse message ID
    message_id = int(parts[2])

    min_timestamp = min(min_timestamp, timestamp)
    min_message_id = min(min_message_id, message_id)
    
    records.append(ProxyRecord(timestamp, message_type, message_id))
    L = f.readline()

requests = list(filter(lambda r: r.type == 'req', records))
responses = list(filter(lambda r: r.type == 'res', records))

ic(len(requests))
ic(len(responses))

groupings = [(requests, 'bo', 'Requests'), 
             (responses, 'ro', 'Responses')]

for collection, color, label in groupings:
  timestamps = list(map(lambda r: r.timestamp - min_timestamp, collection))
  message_ids = list(map(lambda r: r.message_id - min_message_id, collection))
  plt.plot(message_ids, timestamps, color, label=label)

plt.title('CoAP-HTTP Proxy Messages: Message ID vs Time')
plt.xlabel('Message ID [int]')
plt.ylabel('Time [sec]')
plt.legend()
plt.show()