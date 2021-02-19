import csv
import argparse
import ciso8601

import pandas as pd

def parse_args():
  parser = argparse.ArgumentParser(description = '')

  parser.add_argument('-i', '--infiles', dest='infiles',
                      help='', action='store', type=str)
  parser.add_argument('-o', '--outfile', dest='outfile',
                      help='', action='store', type=str)

  return parser.parse_args()

args = parse_args()

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

def parse_protocol_information(fieldmap, parts):
  protocol = fieldmap['message_protocol']

  if protocol == "coap":
    try:
      COAP_TYPE = 0
      # Then there's the MID header
      COAP_MID  = 2
      COAP_CODE = 3

      # Message Type
      coap_type = parts[COAP_TYPE]
      fieldmap['coap_type'] = coap_type
      
      # Message ID
      coap_message_id = parts[COAP_MID]
      fieldmap['coap_message_id'] = coap_message_id

      # Message Code
      coap_code = parts[COAP_CODE]
      fieldmap['coap_code'] = coap_code

      # Message Token
      COAP_TKN = COAP_CODE + 1
      while parts[COAP_TKN] != 'tkn':
        COAP_TKN += 1
      COAP_TKN += 1 # Go to first byte
      coap_token = ""
      for i in range(COAP_TKN, len(parts)):
        if len(parts[i]) == 2:
          coap_token += parts[i]
      fieldmap['coap_token'] = coap_token
    except IndexError as e:
      # print(parts)
      raise e

  elif protocol == "http":
    http_code = parts[0]
    http_resource = parts[1]
    if http_code == "get":
      # Only support HTTP requests, since responses don't have URI in tshark
      fieldmap['http_code'] = http_code
      fieldmap['http_resource'] = http_resource

  else:
    raise ValueError(f"Uncrecognized protocol {protocol}")

def process_line(writer, fieldmap, line):
  # Structure of a tshark line entry
  TSHARK_TIME  = 1
  TSHARK_SRC   = 2
  # Then there is a →
  TSHARK_DST   = 4
  TSHARK_PROTO = 5
  TSHARK_SIZE  = 6
  TSHARK_INFO  = 7

  line = line.lower()
  line = line.replace(",", "")
  line = line.replace(":", " ")
  parts = line.split()
  
  # Timestamp
  message_timestamp = parts[TSHARK_TIME]
  if float(message_timestamp) <= 0:
    raise ValueError(f"Expected positive timestamp, got {message_timestamp}")
  fieldmap['message_timestamp'] = message_timestamp

  # Source
  message_source = parts[TSHARK_SRC]
  fieldmap['message_source'] = message_source

  # Destination
  message_destination = parts[TSHARK_DST]
  fieldmap['message_destination'] = message_destination

  # Protocol
  message_protocol = parts[TSHARK_PROTO]
  if message_protocol not in { "coap", "http" }:
    raise ValueError(f"Unrecognized protol {message_protocol}")
  fieldmap['message_protocol'] = message_protocol

  # Message size
  message_size = parts[TSHARK_SIZE]
  if int(message_size) <= 0:
    raise ValueError(f"Expected positive message size, got {message_size}")
  fieldmap['message_size'] = message_size

  # Enagage protocol-specific parsing
  protocol_info_parts = parts[TSHARK_INFO:]
  parse_protocol_information(fieldmap, protocol_info_parts)

  # Write record
  writer.writerow(fieldmap)

# ====================================================================
# ====================================================================
# ====================================================================
# ====================================================================
# ====================================================================
# ====================================================================
# ====================================================================
# ====================================================================

def ingest_tcpdumps(writer, fieldnames, infile_list):
  # Parse node type from filename
  nodes = []
  for infile in infile_list:
    parts = infile.split('/')
    end = parts[-1].index("_dump")
    n = parts[-1][:end]
    nodes.append(n)

  # Process each file
  for infile, node in zip(infile_list, nodes):
    with open(infile, 'r') as inf:
      for L in inf:
        # Write node type
        fieldmap = { f : "" for f in fieldnames }
        fieldmap['node_type'] = node
        
        # Process each line of the file
        process_line(writer, fieldmap, L)
        
if __name__ == "__main__":
  import doctest
  doctest.testmod()

  # Strip mismatched right ; then split
  infile_list = args.infiles.rstrip(';').split(';')

  with open(args.outfile, 'w') as outf:
    # Write fields of the header
    fieldnames = ['node_type',
                  'message_timestamp', 
                  'message_source',
                  'message_destination',
                  'message_protocol',
                  'message_size',
                  'coap_type',
                  'coap_code',
                  'coap_message_id',
                  'coap_token',
                  'http_code',
                  'http_resource']
    writer = csv.DictWriter(outf, fieldnames=fieldnames)
    writer.writeheader()
    
    ingest_tcpdumps(writer, fieldnames, infile_list)