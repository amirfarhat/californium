#!/bin/sh

import os
import sys
import math
import struct
import socket
import random
random.seed(12)
import argparse
import bitstruct

from icecream import ic
ic.configureOutput(includeContext=True)
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
  # Uri-Host: localhost, Uri-Path: coap2http, Proxy-Uri: http://localhost:8000
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

  def __init__(self):
    # Type of message (0-CON, 1-NON, 2-ACK, 3-RST)
    self.message_type = str.upper(args.message_type)
    if self.message_type not in CoAPMessage.COAP_MSG_STR_TO_ID:
      raise ValueError(f'Bad message type. Need one of {self.COAP_MSG_STR_TO_ID.keys()}')
    self.message_type = self.COAP_MSG_STR_TO_ID[self.message_type]

    # Check token and token length
    if args.token is None:
      self.token, self.token_length = self.random_token()
    else:
      if not self.check_token(args.token):
        raise ValueError('Bad token')
      self.token = args.token
      self.token_length = token_to_bytes(self.token)
    assert 0 <= self.token_length <= 8

    # Check code
    self.code = self.code_str_to_int(args.code)

    # Check message ID
    if args.message_id is None:
      args.message_id = self.random_message_id()
    if not CoAPMessage.check_message_id(args.message_id):
      raise ValueError(f'Bad message ID')
    self.message_id = args.message_id

    self.options = OrderedDict()
    self.options['uri_host']  = (3,  args.uri_host),
    self.options['uri_path']  = (11, args.uri_path),
    self.options['proxy_uri'] = (35, args.proxy_uri),

    self.payload = bytes(args.payload, "utf-8")

  def pack(self):
    ic(self.__dict__)
    out = bytes()

    # ------------ Pack header
    
    out += bitstruct.pack(
      "u2u2u4u8u16",
      self.COAP_VERSION,
      self.message_type,
      self.token_length,
      self.code,
      self.message_id,
    )
  
    # ------------ Pack token

    packed_token = struct.pack(f"!{self.token_length}s", self.token)
    out += packed_token

    # ------------ Pack options

    option_number = 3
    option_value = '127.0.0.1'
    option_delta = 3
    option_value_bytes = option_value.encode('utf-8')
    option_length_bytes = len(option_value_bytes)

    # IMPORTANT: NOTE HOW THE BIT SHIFTING IS HAPPENING
    # HERE WITH THE STRUCT PACKAGE TO ACHIEVE THE DESIRING
    # BIT-LEVEL PACKING. IDEA/TODO: DO THIS WITH THE HEADER
    # SINCE THE STRUCT PACKAGE SEEMS MUCH MORE RELIBALE (STDLIB) 
    packed_options = struct.pack(
      f"!B{option_length_bytes}s",
      (option_delta << 4) | option_length_bytes,
      option_value_bytes
    )

    out += packed_options
    
    return out

    """
    # Now pack options
    last_option_number = 0
    for option_name, option_tuple in self.options.items():
      option_number, option_value = option_tuple[0]
      dprint(f"Packing {option_name} ({option_number})...")

      # Write 4-bit option delta
      option_delta = option_number - last_option_number
      option_delta_nibble = self._get_option_nibble(option_delta)
      out += bitstruct.pack("u4", option_delta_nibble)
      dprint(f"Packed option_delta_nibble {option_delta_nibble}...")

      # Write 4-bit option length
      option_value_bytes = option_value.encode('utf-8')
      option_value_bytes_size = len(option_value_bytes)
      option_size_nibble = self._get_option_nibble(option_value_bytes_size)
      out += bitstruct.pack("u4", option_size_nibble)
      dprint(f"Packed option_size_nibble {option_size_nibble} from option size {option_value_bytes_size} bytes...")

      # Note: Options 13, 14, 15 require more serialization
      if option_number in [13, 14, 15]:
        raise NotImplementedError()

      # Write option value
      out += bitstruct.pack(f"r{option_value_bytes_size}", option_value_bytes)
      dprint(f"Packed {option_name} as value {option_value} with size {option_value_bytes_size} bytes")
      
      last_option_number = option_number

      break
    """

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
    int_token = int.from_bytes(token, byteorder=sys.byteorder)
    return 0 <= int_token <= cls.MAX_TOKEN

  @classmethod
  def random_token(cls) -> (bytes, int):
    """
    Return a new random token
    """
    num_bytes = random.randint(1, 8)
    return os.urandom(num_bytes), num_bytes
  
  @classmethod
  def check_message_id(cls, mid):
    """
    Return True if input message ID `mid` is valid message ID
    and False otherwise
    """
    return cls.NONE <= mid <= cls.MAX_MESSAGE_ID

  @classmethod
  def random_message_id(cls, mid):
    """
    Return a new message ID sampled randomly from [0, MAX_MESSAGE_ID]
    """
    raise NotImplementedError()

def create_socket():
  """
  Create an IPv4 socket
  """
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  # sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
  # sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
  sock.bind((args.source, args.src_port))
  return sock

def generate_coap_packet():
  coap_msg = CoAPMessage()
  packed_coap = coap_msg.pack()
  return packed_coap

def send_coap_packet(sock, packet):
  try:
    ic(f"Using socket {sock}")
    ic(f"Sending to {args.destination}:{args.dst_port}")
    out = sock.sendto(packet, (args.destination, args.dst_port))
    ic(f"Sock output: {out}")
  except() as e:
    print('Failed to send packet', e)

def main():
  sock = create_socket()
  packet = generate_coap_packet()
  send_coap_packet(sock, packet)

if __name__ == "__main__":
  import doctest
  doctest.testmod()
  main()