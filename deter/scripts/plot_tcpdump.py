import argparse
import ciso8601

import matplotlib.pyplot as plt

from collections import namedtuple
from collections import OrderedDict
from recordclass import recordclass

def parse_args():
  parser = argparse.ArgumentParser(description = '')
  parser.add_argument('-a', '--processed-attacker-dump', dest='processed_attacker_dump',
                      help='', action='store', type=str)
  parser.add_argument('-p', '--processed-proxy-dump', dest='processed_proxy_dump',
                      help='', action='store', type=str)
  parser.add_argument('-l', '--proxy-log', dest='proxy_log',
                      help='', action='store', type=str)
  parser.add_argument('-g', '--graph', dest='graph', action='store_true')
  return parser.parse_args()

args = parse_args()

MAX_READ=float('inf')
Message = namedtuple('Message', 'uid dt')
uid_extractor = lambda msg : msg.uid
dt_extractor = lambda msg : msg.dt

ProxyRecord = recordclass('ProxyRecord', 'coap_recv coap_translate http_recv http_translate http_fail ')

min_timestamp = float('inf')
proxy_records = OrderedDict()
uid_map = dict()
attacker_messages = []
proxy_messages = []

recvd_proxy_uids = set()
to_http_translated_proxy_uids = set()
responded_http_proxy_uids = set()
to_coap_translated_proxy_uids = set()

def parse_from_tshark_line(message_string):
  # Format: 1 2021-01-30 20:01:34.198559      8.8.8.8 → 10.1.1.3     CoAP 92 CON MID:7058 GET TKN:a8 33 65 1b coap://10.1.1.3/coap2http
  message_string = message_string.replace(',', '')
  parts = message_string.split()

  MID_IDX = 9
  TKN_IDX = 11
  TIME_IDXS = [1, 2]

  # Parse time
  time_string = " ".join(parts[i] for i in TIME_IDXS)
  message_dt = ciso8601.parse_datetime(time_string)
  
  # Parse message ID
  if not parts[MID_IDX].startswith('MID:'):
    raise ValueError(parts[MID_IDX])
  mid_string = parts[MID_IDX].replace('MID:', '')

  # Parse token
  if not parts[TKN_IDX].startswith('TKN:'):
    raise ValueError(parts[TKN_IDX])
  token_string = parts[TKN_IDX].replace('TKN:', '')
  # Accumulate token pieces
  for i in range(TKN_IDX + 1, len(parts)):
    if parts[i].startswith('coap://'):
      # Skip options
      break
    token_string += parts[i]

  # Construct message UID
  message_uid = f"{mid_string}_{token_string}"
  
  return message_dt, message_uid

def ingest_tcpdump(dump_file, message_collection):
  with open(dump_file, 'r') as f:
    L = f.readline()
    i = 0
    while L:
      if i > MAX_READ:
        break
      message_dt, message_uid = parse_from_tshark_line(L)
      if message_uid not in uid_map:
        uid_map[message_uid] = len(uid_map)
      message_collection.append(Message(dt=message_dt, uid=message_uid))
      L = f.readline()
      i += 1

def ingest_proxy_log(proxy_log, records):
  with open(proxy_log, 'r') as f:
    L = f.readline()
    while L:
      # Line must be a custom debugging statement
      dbg = L.replace("[DBG] ", "")
      if len(dbg) < len(L):
        # Parse log line
        # Format: [DBG] 2021-31-01 00:00:50543 HTTP_RECVD_SUCCESS 29615_CD29DAF9
        parts = dbg.split()
        event = parts[1]
        request_handle = parts[2].lower()
        # dt=ciso8601.parse_datetime(time_string)

        if event == "COAP_RECEIVED":
          # proxy_records[request_handle] = ProxyRecord(\
          #   coap_recv=dt,
          #   coap_translate=None,
          #   http_recv=None,
          #   http_translate=None,
          #   http_fail=True,
          # )
          recvd_proxy_uids.add(request_handle)
          
        elif event == "COAP_TRANSLATED":
          # proxy_records[request_handle].coap_translate = dt
          to_http_translated_proxy_uids.add(request_handle)

        elif event == "HTTP_RECVD_SUCCESS":
          # proxy_records[request_handle].http_recv = dt
          # proxy_records[request_handle].http_fail = False
          responded_http_proxy_uids.add(request_handle)

        elif event == "HTTP_TRANSLATED":
          # proxy_records[request_handle].http_translate = dt
          to_coap_translated_proxy_uids.add(request_handle)

        elif event == "HTTP_RECVD_FAILED":
          # proxy_records[request_handle].http_recv = dt
          pass

        elif event == "HTTP_RECVD_CANCELLED":
          # proxy_records[request_handle].http_recv = dt
          pass

        else:
          raise Exception(f"Got {L}")

      L = f.readline()

# Ingest attacker dump
ingest_tcpdump(args.processed_attacker_dump,  attacker_messages)

# Ingest proxy dump
ingest_tcpdump(args.processed_proxy_dump,  proxy_messages)

# Ingest proxy log
ingest_proxy_log(args.proxy_log, proxy_records)

attacker_dump_uids = set(map(uid_extractor, attacker_messages))
num_attacker_dump_uids = len(attacker_dump_uids)
proxy_dump_uids = set(map(uid_extractor, proxy_messages))

print(f"{100 * len(attacker_dump_uids & attacker_dump_uids) / num_attacker_dump_uids}% attacker --> attacker")
print(f"{100 * len(attacker_dump_uids & proxy_dump_uids) / num_attacker_dump_uids}% attacker --> proxy interface")
print(f"{100 * len(attacker_dump_uids & recvd_proxy_uids) / num_attacker_dump_uids}% attacker --> proxy coap stack")
print(f"{100 * len(attacker_dump_uids & to_http_translated_proxy_uids) / num_attacker_dump_uids}% attacker --> proxy translate to http")
print(f"{100 * len(attacker_dump_uids & responded_http_proxy_uids) / num_attacker_dump_uids}% attacker --> proxy server round trip")
print(f"{100 * len(attacker_dump_uids & to_coap_translated_proxy_uids) / num_attacker_dump_uids}% attacker --> proxy translate to coap")

if args.graph:
  attacker_message_nums = [uid_map[m.uid] for m in attacker_messages]
  attacker_dts = list(map(dt_extractor, attacker_messages))

  proxy_message_nums = [uid_map[m.uid] for m in proxy_messages]
  proxy_dts = list(map(dt_extractor, proxy_messages))

  plt.plot(attacker_message_nums, attacker_dts, label="Attacker Dump")
  plt.plot(proxy_message_nums, proxy_dts, label="Proxy Dump")
  plt.legend()
  
  plt.show()
