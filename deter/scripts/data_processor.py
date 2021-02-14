import csv
import argparse
import ciso8601

import pandas as pd

def parse_args():
  parser = argparse.ArgumentParser(description = '')

  parser.add_argument('-t', '--data-type', dest='data_type',
                      help='', action='store', type=str.lower, choices=["attacker_dump", "proxy_dump", "receiver_dump", "client_dump", "proxy_log"])

  parser.add_argument('-i', '--infile', dest='infile',
                      help='', action='store', type=str)
  parser.add_argument('-o', '--outfile', dest='outfile',
                      help='', action='store', type=str)

  return parser.parse_args()

args = parse_args()

ALLOWED_EVENTS={
  "coap_received",
  "coap_translated",
  "http_recvd_success",
  "http_translated",
  "http_recvd_failed",
  "http_recvd_cancelled",
}

class ProxyLogLineDebugFormatException(Exception): pass
class ProxyLogEventException(Exception): pass
class ProxyLogValueException(Exception): pass

# ====================================================================
# ====================================================================
# ====================================================================
# ====================================================================
# ====================================================================
# ====================================================================
# ====================================================================
# ====================================================================

def parse_from_tshark_line(message_string):
  """
  # ---------------- Attacker / Proxy

  >>> parse_from_tshark_line("34 1612380142.546438      8.8.8.8 → 10.1.1.3     CoAP 92 CON, MID:4314, GET, TKN:23 5c 2f b7, coap://10.1.1.3/coap2http")
  ('1612380142.546438', '4314', '235c2fb7', 'GET')
  
  >>> parse_from_tshark_line("437298 1612380162.414260      8.8.8.8 → 10.1.1.3     CoAP 92 CON, MID:50693, GET, TKN:cf fe a6 6c, coap://10.1.1.3/coap2http")
  ('1612380162.414260', '50693', 'cffea66c', 'GET')
  
  # ---------------- Receiver

  >>> parse_from_tshark_line("31434 1612992383.976399     10.1.1.2 → 10.1.1.3     CoAP 183 ACK, MID:59721, 2.05 Content, TKN:be e3 9e 2e")
  ('1612992383.976399', '59721', 'bee39e2e', '2.05')
  
  >>> parse_from_tshark_line("31435 1612992383.995075     10.1.1.2 → 10.1.1.3     CoAP 62 ACK, MID:59785, 5.02 Bad Gateway, TKN:04 4d eb 22")
  ('1612992383.995075', '59785', '044deb22', '5.02')

  # ---------------- Client

  >>> parse_from_tshark_line("67135 1613161431.703387     10.1.1.2 → 10.1.1.3     CoAP 88 CON, MID:33568, GET, TKN:93 48 5b a2 53 52 fc d6, /coap2http")
  ('1613161431.703387', '33568', '93485ba25352fcd6', 'GET')

  >>> parse_from_tshark_line("67137 1613161431.706885     10.1.1.2 → 10.1.1.3     CoAP 88 CON, MID:33569, GET, TKN:23 5c df f3 fb f2 db fc, /coap2http")
  ('1613161431.706885', '33569', '235cdff3fbf2dbfc', 'GET')
  
  >>> parse_from_tshark_line("67136 1613161431.706736     10.1.1.3 → 10.1.1.2     CoAP 187 ACK, MID:33568, 2.05 Content, TKN:93 48 5b a2 53 52 fc d6, /coap2http")
  ('1613161431.706736', '33568', '93485ba25352fcd6', '2.05')
  
  >>> parse_from_tshark_line("67138 1613161431.738468     10.1.1.3 → 10.1.1.2     CoAP 62 ACK, MID:33569, 5.02 Bad Gateway, TKN:23 5c df f3 fb f2 db fc, /coap2http")
  ('1613161431.738468', '33569', '235cdff3fbf2dbfc', '5.02')
  >>>
  """
  # Normal Format: 1 1612380142.546085      8.8.8.8 → 10.1.1.3     CoAP 92 CON, MID:4281, GET, TKN:f4 22 27 39, coap://10.1.1.3/coap2http
  # Recv   Format: 31435 1612992383.995075     10.1.1.2 → 10.1.1.3     CoAP 62 ACK, MID:59785, 5.02 Bad Gateway, TKN:04 4d eb 22
  parts = message_string.split()

  # Set parsing parameters
  TSHARK_TIME_IDX = 1
  TSHARK_MID_IDX = 8
  TSHARK_CODE_IDX = 9

  # Parse time
  message_timestamp = parts[TSHARK_TIME_IDX]
  if float(message_timestamp) <= 0:
    raise ValueError(f"Expected positive timestamp, got {message_timestamp}")

  # Parse message ID
  if not parts[TSHARK_MID_IDX].startswith('MID:'):
    raise ValueError(parts[TSHARK_MID_IDX])
  message_id = parts[TSHARK_MID_IDX][4:-1] # Skip prefix and last comma

  # Parse code
  if parts[TSHARK_CODE_IDX].endswith(','):
    message_code = parts[TSHARK_CODE_IDX][:-1] # Skip comma
  else:
    message_code = parts[TSHARK_CODE_IDX]

  # Find token start
  TSHARK_TKN_IDX = None
  for i in range(TSHARK_CODE_IDX, len(parts)):
    if parts[i].startswith('TKN:'):
      TSHARK_TKN_IDX = i
      break
  if not parts[TSHARK_TKN_IDX].startswith('TKN:'):
    raise ValueError(parts)
  message_token = parts[TSHARK_TKN_IDX].replace('TKN:', '')

  # Accumulate token pieces
  for i in range(TSHARK_TKN_IDX + 1, len(parts)):
    if parts[i].startswith('coap://') or parts[i].startswith('/coap2http'):
      # Skip options
      break
    message_token += parts[i].strip(',')

  return message_timestamp, message_id, message_token, message_code

def parse_from_proxy_log(log_line):
  """
  >>> parse_from_proxy_log("[DBG] 1612380142674 COAP_RECEIVED 4287_2236F256")
  ('1612380142.674', '4287', '2236f256', 'coap_received')

  >>> parse_from_proxy_log("[DBG] 1612380204860 HTTP_RECVD_FAILED 29824_744CEDC8")
  ('1612380204.860', '29824', '744cedc8', 'http_recvd_failed')
  """
  # Line must be a custom debugging statement
  if not log_line.startswith("[DBG]"):
    raise ProxyLogLineDebugFormatException("Expected log line to start with: [DBG]")

  # Parse log line. Example format:
  # [DBG] 1612380142674 COAP_RECEIVED 4287_2236F256
  # [DBG] 1612380204860 HTTP_RECVD_FAILED 29824_744CEDC8

  parts = log_line.split()
  if len(parts) != 4:
    raise ProxyLogValueException(f"Expected log line with 4 parts, got {log_line}")

  # Parse timestamp - millis since epoch
  timestamp_ms = int(parts[1])
  if timestamp_ms <= 0:
    raise ProxyLogValueException(f"Got weird millisecond timestamp {timestamp_ms}")
  # Convert to sec with decimal ==> separate on last three least significant digits
  timestamp = f"{timestamp_ms // 1000}.{timestamp_ms % 1000}"

  # Parse event
  event = parts[2].lower()
  if event not in ALLOWED_EVENTS:
    raise ProxyLogValueException(f"Got unkown proxy event {event}")

  # Parse request handle, a concat of message ID and token
  request_handle = parts[3].lower()
  message_id, token = request_handle.split("_")

  return timestamp, message_id, token, event

# ====================================================================
# ====================================================================
# ====================================================================
# ====================================================================
# ====================================================================
# ====================================================================
# ====================================================================
# ====================================================================

def ingest_tcpdump(infile, outfile):
  with open(outfile, 'w') as outf:
    # Write fields of the header
    fieldnames = ['message_timestamp', 'message_id', 'message_token', 'event']
    writer = csv.DictWriter(outf, fieldnames=fieldnames)
    writer.writeheader()

    with open(infile, 'r') as inf:
      for L in inf:
        try: 
          # Parse fields from input file
          mtimestamp, mid, mtoken, mcode = parse_from_tshark_line(L)
          
          # Write fields to output file
          writer.writerow({'message_timestamp': mtimestamp,
                            'message_id': mid,
                            'message_token': mtoken,
                            'event': mcode})
        except ProxyLogLineDebugFormatException:
          # Prefix of log with Java start output --> can skip
          continue

def ingest_proxy_log(infile, outfile):
  with open(outfile, 'w') as outf:
    # Write fields of the header
    fieldnames = ['message_timestamp', 'message_id', 'message_token', 'event']
    writer = csv.DictWriter(outf, fieldnames=fieldnames)
    writer.writeheader()

    with open(infile, 'r') as inf:
      for L in inf:
        try:
          # Parse fields from input file
          mtimestamp, mid, mtoken, mevent,  = parse_from_proxy_log(L)
          
          # Write fields to output file
          writer.writerow({'message_timestamp': mtimestamp,
                            'message_id': mid,
                            'message_token': mtoken,
                            'event': mevent})
        except ProxyLogLineDebugFormatException:
          # Skip prefix log lines from Java and Californium startup
          continue
        
if __name__ == "__main__":
  import doctest
  doctest.testmod()

  if args.data_type.endswith("_dump"):
    ingest_tcpdump(args.infile, args.outfile)
  else:
    ingest_proxy_log(args.infile, args.outfile)