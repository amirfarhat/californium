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

def parse_protocol_information(fieldmap, row, uid_map_number):
  protocol = fieldmap['message_protocol']
  uid = None

  if protocol == "coap":
    # Core CoAP Fields
    fieldmap["coap_type"] = row["coap.type"]
    fieldmap["coap_code"] = row["coap.code"]
    fieldmap["coap_message_id"] = row["coap.mid"]
    fieldmap["coap_token"] = row["coap.token"]

    # TODO Transform code into c.dd format

    # CoAP Options
    fieldmap["coap_proxy_uri"] = row["coap.opt.proxy_uri"]

    # Uid is made from the CoAP message ID and token
    coap_message_id = fieldmap["coap_message_id"]
    coap_token = fieldmap["coap_token"]
    uid = f"{coap_message_id}_{coap_token}".lower()
    if ":" in uid or ":" in coap_token:
      print(coap_token)
      print(uid)
      print(list(uid_map_number.items())[:20])
      raise Exception()

  elif protocol == "http":
    # Is HTTP request?
    fieldmap["http_request"] = row["http.request"]
    fieldmap["http_request_method"] = row["http.request.method"]
    fieldmap["http_request_full_uri"] = row["http.request.full_uri"]

    # Is HTTP response?
    fieldmap["http_response"] = row["http.response"]
    fieldmap["http_response_code"] = row["http.response.code"]
    fieldmap["http_response_code_desc"] = row["http.response.code.desc"]
    fieldmap["http_response_for_uri"] = row["http.response_for.uri"]

    # TODO lowercase the request method

    # Get whichever URI is first and not empty string
    uri = fieldmap["http_request_full_uri"] or fieldmap["http_response_for_uri"]

    # Uid (from CoAP message ID and token), is the requested resource
    uid = uri.split("/")[-1].lower()

  else:
    raise ValueError(f"Uncrecognized protocol {protocol}")

  # Add to uid map
  uid_map_number.setdefault(uid, 1 + len(uid_map_number))
  fieldmap["message_number"] = uid_map_number[uid]

def process_row(row, writer, fieldmap, uid_map_number):
  # Timestamp
  message_timestamp = row["_ws.col.Time"]
  if float(message_timestamp) <= 0:
    raise ValueError(f"Expected positive timestamp, got {message_timestamp}")
  fieldmap["message_timestamp"] = message_timestamp

  # Source
  message_source = row["_ws.col.Source"]
  fieldmap["message_source"] = message_source

  # Destination
  message_destination = row["_ws.col.Destination"]
  fieldmap["message_destination"] = message_destination

  # Protocol
  message_protocol = row["_ws.col.Protocol"].lower()
  if message_protocol not in { "coap", "http" }:
    raise ValueError(f"Unrecognized protol {message_protocol}")
  fieldmap["message_protocol"] = message_protocol

  # Message size
  message_size = row["_ws.col.Length"]
  if int(message_size) <= 0:
    raise ValueError(f"Expected positive message size, got {message_size}")
  fieldmap["message_size"] = message_size

  # Enagage protocol-specific parsing
  parse_protocol_information(fieldmap, row, uid_map_number)
  
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
  nodes = dict()
  for infile in infile_list:
    parts = infile.split('/')
    end = parts[-1].index("_dump")
    n = parts[-1][:end]
    nodes[infile] = n

  # Process each file
  uid_map_number = dict()
  for infile in sorted(infile_list):
    # Process attacker firrst for uid map
    node = nodes[infile]
    with open(infile, 'r') as inf:
      reader = csv.DictReader(inf, delimiter=";", quotechar='"')
      for row in reader:
        fieldmap = { f : "" for f in fieldnames }
        fieldmap['node_type'] = node
        fieldmap['message_number'] = -1

        process_row(row, writer, fieldmap, uid_map_number)
        
if __name__ == "__main__":
  import doctest
  doctest.testmod()

  fieldnames = ['node_type',
                'message_number',
                'message_timestamp', 
                'message_source',
                'message_destination',
                'message_protocol',
                'message_size',
                'coap_type',
                'coap_code',
                'coap_message_id',
                'coap_token',
                'coap_proxy_uri',
                'http_request',
                'http_request_method',
                'http_request_full_uri',
                'http_response',
                'http_response_code',
                'http_response_code_desc',
                'http_response_for_uri']

  # Strip mismatched right ; then split
  infile_list = args.infiles.rstrip(';').split(';')

  with open(args.outfile, 'w') as outf:
    # Write fields of the header
    writer = csv.DictWriter(outf, fieldnames=fieldnames)
    writer.writeheader()
  
    # Process the input files
    ingest_tcpdumps(writer, fieldnames, infile_list)