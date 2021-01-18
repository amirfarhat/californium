#!/bin/sh

import sys
import math
import socket
import argparse
import bitstruct

from pprint import pprint
from struct import pack, unpack

def parse_args():
  """
  Handle command-line arguments
  """
  parser = argparse.ArgumentParser(description = 'CoAP-over-UDP Message Spoofer and Sender')
  parser.add_argument('-x', '--debug', dest='debug',
                      help='Enable debug mode.  Print packets before trying to send',
                      action='store_true', default=False)

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
  parser.add_argument('-o', '--options', dest='options',
                      help='Options block include in the CoAP Message to send',
                      nargs='?', action='store', default="", type=str)
  parser.add_argument('-p', '--payload', dest='payload',
                      help='Payload of the CoAP Message to send',
                      nargs='?', action='store', default="", type=str)
  return parser.parse_args()
  
args = parse_args()

def dprint(*fargs, **kwargs):
  if args.debug:
    print(*fargs, **kwargs)

def dpprint(*fargs, **kwargs):
  if args.debug:
    pprint(*fargs, **kwargs)

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
  def __init__(self):
    self.ihl = 5
    self.version = 4
    self.tos = 0
    self.tot_len = 20 + 20
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
      p = pack(
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
      p = pack(
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
    return pack(
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

    # Check token and make token length
    if not self.check_token(args.token):
      raise ValueError('Bad token')
    self.token = args.token
    
    # The token's length (in bytes) must be between 0 and 8
    self.token_length = token_to_bytes(args.token)
    assert 0 <= self.token_length <= 8

    # Check code
    self.code = self.code_str_to_int(args.code)

    # Check message ID
    if args.message_id is None:
      args.message_id = self.random_message_id()
    if not CoAPMessage.check_message_id(args.message_id):
      raise ValueError(f'Bad message ID')
    self.message_id = args.message_id

    self.options = args.options
    self.payload = bytes(args.payload, "utf-8")

  def pack(self):
    value_map = {
      'version'      : self.COAP_VERSION,
      'type'         : self.message_type,
      'token_length' : self.token_length,
      'code'         : self.code,
      'message_id'   : self.message_id,
    }
    rep_map = {
      'version'      : 'u2',
      'type'         : 'u2',
      'token_length' : 'u4',
      'code'         : 'u8',
      'message_id'   : 'u16',
    }
    
    fields = ['version', 'type', 'token_length', 'code', 'message_id']
    reps = "".join(rep_map[f] for f in fields)
    return bitstruct.pack_dict(reps, fields, value_map)

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
  def check_token(cls, token):
    """
    Return True if input token `token` is valid and False otherwise
    """
    return 0 <= token <= cls.MAX_TOKEN

  @classmethod
  def random_token(cls, mid):
    """
    Return a new token sampled randomly from [0, MAX_TOKEN]
    """
    raise NotImplementedError()
  
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
  return sock

def generate_coap_packet():
  coap_msg = CoAPMessage()
  dpprint(coap_msg.__dict__)
  packed_coap = coap_msg.pack()

  udp_pkt = UDPPacket(packed_coap)
  # udp_pkt = UDPPacket(data=bytes('x', 'utf-8'))
  packed_udp = udp_pkt.pack()

  ip_hdr = IPv4Header()
  packed_ip_hdr = ip_hdr.pack()

  packet = packed_ip_hdr + packed_udp
  return packed_coap

def send_coap_packet(socket, packet):
  try:
    dprint(f"Using socket {socket}")
    dprint(f"Sending to {args.destination}:{args.dst_port}")
    out = socket.sendto(packet, (args.destination, args.dst_port))
    dprint(f"Socket output: {out}")
  except() as e:
    print('Failed to send packet', e)

def main():
  socket = create_socket()
  packet = generate_coap_packet()
  send_coap_packet(socket, packet)

if __name__ == "__main__":
  import doctest
  doctest.testmod()
  main()