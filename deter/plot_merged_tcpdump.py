import csv
import argparse

import matplotlib.pyplot as plt

from icecream import ic
from collections import OrderedDict
from recordclass import recordclass

def parse_args():
  parser = argparse.ArgumentParser(description = 'Plot sequence graph from pcaps on two machines')
  parser.add_argument('-w', '--wireshark-csv', dest='wireshark_csv',
                      help='CSV file from wireshark', action='store', type=str)
  parser.add_argument('-g', '--graph', dest='graph', action='store_true')
  return parser.parse_args()

args = parse_args()

def parse_info_from_string(info_string):
  info_string = info_string.replace(',', '')
  parts = info_string.split()

  if not parts[0].startswith('CON'):
    raise ValueError(parts[0])

  # Parse message ID
  if not parts[1].startswith('MID:'):
    raise ValueError(parts[1])
  mid_string = parts[1].replace('MID:', '')

  # Parse token
  if not parts[3].startswith('TKN:'):
    raise ValueError(parts[3])
  token_string = parts[3].replace('TKN:', '')
  # Accumulate token pieces
  for i in range(4, len(parts)):
    if parts[i].startswith('coap://'):
      # Skip options
      break
    token_string += parts[i]

  return f"{mid_string}_{token_string}"
      
records = OrderedDict()

PacketRecord = recordclass('PacketRecord', 'first_timestamp second_timestamp')

with open(args.wireshark_csv, 'r') as f:
  reader = csv.reader(f)
  
  for i, row in enumerate(reader):
    if i == 0:
      # Skip header
      continue

    time_sec = float(row[1])
    info_string = row[-1]
    message_uid = parse_info_from_string(info_string)

    if message_uid not in records:
      records[message_uid] = PacketRecord(\
        first_timestamp  = time_sec,
        second_timestamp = None
      )
    else:
      records[message_uid].second_timestamp = time_sec
    
    # if i == 100:
    #   break

# Convert messages from uid to int
message_numbers = []
first_timestamps = []
second_timestamps = []
for i, t in enumerate(records.items()):
  uid, record = t
  message_numbers.append(i)
  first_timestamps.append(record.first_timestamp)
  second_timestamps.append(record.second_timestamp)

plt.plot(message_numbers, first_timestamps, 'bo', label="Attacker Timestamp")

plt.plot(message_numbers, second_timestamps, 'ro', label="Proxy Timestamp")

plt.xlabel("Message Index")
plt.ylabel("Time [sec]")
plt.title("CoAP Packet Timestamps")

plt.legend()
plt.show()