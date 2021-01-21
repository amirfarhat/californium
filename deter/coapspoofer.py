#!/bin/sh

import os
import sys
import math
import time
import struct
import socket
import random
import argparse

from pprint import pprint
from collections import OrderedDict

def parse_args():
  """
  Handle command-line arguments
  """
  parser = argparse.ArgumentParser(description = 'CoAP-over-UDP Message Spoofer and Sender')
  parser.add_argument('-x', '--debug', dest='debug',
                      help='Enable debug mode.  Print packets before trying to send',
                      action='store_true', default=False)

  # IP + UDP
  parser.add_argument('-s', '--source', dest='source',
                      help='Source Address',
                      action='store', default='127.0.0.1', type=str)
  parser.add_argument('-S', '--src-port', dest='src_port',
                      help='Source Port',
                      action='store', default=132, type=int)
  parser.add_argument('-d', '--destination', dest='destination',
                      help='Destination Address',
                      action='store', default='127.0.0.1', type=str)
  parser.add_argument('-D', '--dst-port', dest='dst_port',
                      help='Destination Port',
                      action='store', default=80, type=int)

  # CoAP Header
  parser.add_argument('-m', '--message-id', dest='message_id',
                      help='ID of the CoAP Message to send',
                      action='store', default=None, type=int)
  parser.add_argument('-M', '--message-type', dest='message_type',
                      help='Type of the CoAP Message to send, one of (CON|NON|ACK|RST)',
                      action='store', default=0, type=str)
  parser.add_argument('-t', '--token', dest='token',
                      help='Token of the CoAP Message to send',
                      action='store', default=None, type=int)
  parser.add_argument('-c', '--code', dest='code',
                      help='Code of the CoAP Message to send',
                      action='store', default='000', type=str)
  
  # CoAP Options - Proxying
  parser.add_argument('-u', '--uri-host', dest='uri_host',
                      help='The Uri-Host Option specifies the Internet host of the resource being requested',
                      nargs='?', action='store', default="127.0.0.1", type=str)
  parser.add_argument('-a', '--uri-path', dest='uri_path',
                      help='The Uri-Path Option specifies one segment of the absolute path to the resource',
                      nargs='?', action='store', default="coap2http", type=str)
  parser.add_argument('-y', '--proxy-uri', dest='proxy_uri',
                      help='The Proxy-Uri Option is used to make a request to a forward-proxy',
                      nargs='?', action='store', default="http://localhost:8000", type=str)
  
  # CoAP Payload
  parser.add_argument('-p', '--payload', dest='payload',
                      help='Payload of the CoAP Message to send',
                      nargs='?', action='store', default="", type=str)

  # Meta Information
  parser.add_argument('-f', '--flood', dest='flood',
                      help='Flag indicating whether to send packets at line rate',
                      nargs='?', action='store', default=False, type=bool)
  parser.add_argument('-n', '--num-messages', dest='num_messages',
                      help='Number of packets to send. Cannot also be used with the flood option',
                      nargs='?', action='store', default=-1, type=int)

  return parser.parse_args()
  
args = parse_args()

# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------

def token_to_bytes(token):
  """
  Return the number of bytes in int `token`

  >>> token_to_bytes(0)
  0
  >>> token_to_bytes(0x055B23FA)
  4
  >>> token_to_bytes(0x2EB1FAA)
  4
  >>> token_to_bytes(0x91600E)
  3
  >>> token_to_bytes(0x28BC7F)
  3
  >>> token_to_bytes(1 << 64 - 1)
  8
  """
  if token == 0:
    return 0
  # Subtract away the initial '0b' from length
  bits = len(bin(token)) - 2
  return math.ceil(bits / 8)

class IPv4Header:
  """
  Header of an IPv4 Packet
  """
  def __init__(self, payload):
    assert isinstance(payload, bytes)
    self.ihl = 5
    self.version = 4
    self.tos = 0
    self.tot_len = 20 + len(payload)
    self.id = 54321
    self.frag_off = 0
    self.ttl = 255
    self.protocol = socket.IPPROTO_UDP
    self.check = 10
    self.saddr = socket.inet_aton(args.source)
    self.daddr = socket.inet_aton(args.destination)
    self.ihl_version = (self.version << 4) + self.ihl

  def pack(self):
    if 'freebsd' in sys.platform.lower():
      #In FreeBSD, the length and offset fields must be provided in host-byte (little-endian) order
      p = struct.pack(
          '!BBHHHBBH4s4s',
          self.ihl_version,
          self.tos,
          socket.htons(self.tot_len),
          self.id,
          socket.htons(self.frag_off),
          self.ttl,
          self.protocol,
          self.check,
          self.saddr,
          self.daddr
      )
    else:
      p = struct.pack(
          '!BBHHHBBH4s4s',
          self.ihl_version,
          self.tos,
          self.tot_len,
          self.id,
          self.frag_off,
          self.ttl,
          self.protocol,
          self.check,
          self.saddr,
          self.daddr
      )
    return p

class UDPPacket:
  """
  Represents the packet structure transported by UDP
  """
  def __init__(self, data):
    self.sport = int(args.src_port)
    self.dport = int(args.dst_port)
    self.data = data
    self.ulen = 8 + len(data)
    self.sum = 0
    self.data_len = len(data)

  def pack(self):
    return struct.pack(
      "!HHHH{}s".format(self.data_len),
      self.sport,
      self.dport,
      self.ulen,
      self.sum,
      self.data
    )

class CoAPMessage:
  """
  Represents the message structure transported by CoAP

  Code
    0.00      : Indicates an Empty message
    0.01-0.31 : Indicates a request.  Values in this range are assigned by
                the "CoAP Method Codes" sub-registry 
    1.00-1.31 : Reserved
    2.00-5.31 : Indicates a response.  Values in this range are assigned by
                the "CoAP Response Codes" sub-registry
    6.00-7.31 : Reserved
    
  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
  |Ver| T |  TKL  |      Code     |          Message ID           |
  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
  |   Token (if any, TKL bytes) ...
  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
  |   Options (if any) ...
  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
  |1 1 1 1 1 1 1 1|    Payload (if any) ...
  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
  """
  NONE = -1
  MAX_MESSAGE_ID = (1 << 16) - 1
  MAX_TOKEN = (1 << (8 * 8)) - 1
  CODE_CLASS_BITS = 3
  CODE_DETAIL_BITS = 5
  PAYLOAD_MARKER = 0xFF
  COAP_VERSION = 1
  COAP_MSG_STR_TO_ID = { 'CON':0, 'NON':1, 'ACK':2, 'RST':3 }

  def __init__(self, msg_id=None, proxy_uri_suffix=""):
    if msg_id is None:
      msg_id = args.message_id

    # Type of message (0-CON, 1-NON, 2-ACK, 3-RST)
    self.message_type = str.upper(args.message_type)
    if self.message_type not in CoAPMessage.COAP_MSG_STR_TO_ID:
      raise ValueError(f'Bad message type. Need one of {self.COAP_MSG_STR_TO_ID.keys()}')
    self.message_type = self.COAP_MSG_STR_TO_ID[self.message_type]

    # Check token and token length
    if args.token is None:
      self.token, self.token_length = self.random_token()
    else:
      if not self.check_token(self.token):
        raise ValueError('Bad token')
      self.token = token
      self.token_length = token_to_bytes(self.token)
      
    assert 0 <= self.token_length <= 8

    # Check code
    self.code = self.code_str_to_int(args.code)

    # Check message ID
    if msg_id is None:
      msg_id = self.random_message_id()
    if not CoAPMessage.check_message_id(msg_id):
      raise ValueError(f'Bad message ID')
    self.message_id = msg_id

    # Construct proxy-specific mappings
    self.options = OrderedDict()
    self.options['uri_host']  = (3,  args.uri_host),
    self.options['uri_path']  = (11, args.uri_path),
    self.options['proxy_uri'] = (35, f"{args.proxy_uri}/{proxy_uri_suffix}"),

    self.payload = bytes(args.payload, "utf-8")

  def pack(self):
    out = bytes()

    # Header: 32 bits = 4 bytes
    header = 0
    header = (header << 2) | self.COAP_VERSION
    header = (header << 2) | self.message_type
    header = (header << 4) | self.token_length
    header = (header << 8) | self.code  
    header = (header << 16) | self.message_id
    out += struct.pack("!I", header)
  
    # Token
    packed_token = struct.pack(f"!{self.token_length}s", self.token)
    out += packed_token

    # Options
    last_option_number = 0
    for option_name, option_tuple in self.options.items():
      option_number, option_value = option_tuple[0]
      
      # Compute option delta
      option_delta = option_number - last_option_number

      # Compute option value and length in bytes
      option_value_bytes = option_value.encode('utf-8')
      option_length_bytes = len(option_value_bytes)

      # IMPORTANT: NOTE HOW THE BIT SHIFTING IS HAPPENING
      # HERE WITH THE STRUCT PACKAGE TO ACHIEVE THE DESIRED
      # BIT-LEVEL PACKING. IDEA/TODO: DO THIS WITH THE HEADER
      # SINCE THE STRUCT PACKAGE SEEMS MUCH MORE RELIBALE (STDLIB)
      # See https://tools.ietf.org/html/rfc7252#section-3.1 for extended
      if option_delta < 13 and option_length_bytes < 13:
        packed_option = struct.pack(
          f"!B{option_length_bytes}s",
          (option_delta << 4) | option_length_bytes,
          option_value_bytes
        )
      elif (13 <= option_delta <= 13+0xFF) and (13 <= option_length_bytes <= 13+0xFF):
        D, L = 13, 13
        packed_option = struct.pack(
          f"!BBB{option_length_bytes}s",
          (D << 4) | L,
          option_delta - D,
          option_length_bytes - L,
          option_value_bytes
        )
      else:
        raise NotImplementedError()

      out += packed_option
      last_option_number = option_number
    
    return out

  @classmethod
  def _get_option_nibble(cls, option_value):
    """
    Returns the 4-bit option header value
    """
    if option_value <= 12:
      return option_value
    elif option_value <= 255 + 13:
      return 13
    elif option_value <= 65535 + 269:
      return 14
    raise Exception('Bad option number')

  @classmethod
  def check_code_str(cls, code_str):
    """
    Return True if a CoAP code in string form (ex. "205" response code, 
    "002" method code) matches expected format, False otherwise
    """
    # Require three characters
    if len(code_str) != 3:
      return False
    
    # Require all digits
    if not str.isdigit(code_str):
      return False

    # Split into class and detail
    code_class = int(code_str[0])
    code_detail = int(code_str[1:])

    # Check class and detail
    if (code_class < 0) or (code_class >= (1 << cls.CODE_CLASS_BITS)):
      return False
    if (code_detail < 0) or (code_detail >= (1 << cls.CODE_DETAIL_BITS)):
      return False
  
    return True
  
  @classmethod
  def code_str_to_int(cls, code_str):
    """
    Converts a CoAP code (ex. "205" response code, "002" method code) from
    a raw string into an int

    >>> CoAPMessage.code_str_to_int("000")
    0
    >>> CoAPMessage.code_str_to_int("001")
    1
    >>> CoAPMessage.code_str_to_int("004")
    4
    >>> CoAPMessage.code_str_to_int("205")
    69
    """
    if not cls.check_code_str(code_str):
      raise ValueError("Malformed code string")

    code_class = int(code_str[0])
    code_detail = int(code_str[1:])
    
    code = (code_class << cls.CODE_DETAIL_BITS) | code_detail
    return code
  
  @classmethod
  def check_token(cls, token: bytes):
    """
    Return True if input token `token` is valid and False otherwise
    """
    if not isinstance(token, bytes):
      return False
    int_token = int.from_bytes(token, byteorder=sys.byteorder)
    return 0 <= int_token <= cls.MAX_TOKEN

  @classmethod
  def random_token(cls) -> (bytes, int):
    """
    Return a new random token
    """
    # num_bytes = random.randint(1, 8)
    num_bytes = 4
    return os.urandom(num_bytes), num_bytes
  
  @classmethod
  def check_message_id(cls, mid):
    """
    Return True if input message ID `mid` is valid message ID
    and False otherwise
    """
    return cls.NONE <= mid <= cls.MAX_MESSAGE_ID

  @classmethod
  def random_message_id(cls):
    """
    Return a new message ID sampled randomly from [0, MAX_MESSAGE_ID]
    """
    return random.randint(0, cls.MAX_MESSAGE_ID)

def create_socket():
  """
  Create an IPv4 socket
  """
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  # sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
  # sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
  sock.bind((args.source, args.src_port))
  return sock

def coap_message_generator():
  offset = 0

  # Generate first message
  coap_message = CoAPMessage(proxy_uri_suffix=offset)
  yield coap_message
  
  while True:
    # Fetch previous parameters
    mid = coap_message.message_id

    # Increment previous parameters
    mid = ((mid + 1) % CoAPMessage.MAX_MESSAGE_ID)
    offset += 1

    # Generate next message
    coap_message = CoAPMessage(msg_id=mid, proxy_uri_suffix=offset)
    yield coap_message

def send_coap_message(sock, message):
  packet = message.pack()
  out = sock.sendto(packet, (args.destination, args.dst_port))

def main():
  if args.flood and args.num_messages > 0:
    raise ValueError("Err: Either flood or num_messages, not both")

  sock = create_socket()
  gen = coap_message_generator()

  if args.flood:
    sent = 0
    while True:
      message = next(gen)
      send_coap_message(sock, message)
      sent += 1
      if sent % 1000 == 0:
        print(f"Sent {sent}")
  else:
    for i in range(args.num_messages):
      message = next(gen)
      send_coap_message(sock, message)
    print(f"Sent {args.num_messages}")

if __name__ == "__main__":
  import doctest
  doctest.testmod()
  main()