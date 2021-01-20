"""
Multithreaded HTTP server with artificial delay for requests
Based on https://stackoverflow.com/a/14089457/10028710
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import threading

import time
import socket
import argparse

from struct import pack

def parse_args():
  """
  Handle command-line arguments
  """
  parser = argparse.ArgumentParser(description = 'Launch a multithreaded server with induced artifical delay per request')
  
  parser.add_argument('-p', '--port', dest='port',
                      help='port to launch the server on',
                      action='store', default=8000, type=int)
  parser.add_argument('-d', '--delay', dest='delay',
                      help='Artifical delay to include per request',
                      action='store', default=0, type=float)
  
  args = parser.parse_args()
  return args

args = parse_args()

def be_slow(seconds):
  time.sleep(float(seconds))

class Handler(BaseHTTPRequestHandler):
  def do_GET(self):
    be_slow(args.delay)
    self.send_response(200)
    self.send_header("Content-type", "text/html")
    self.end_headers()
    self.wfile.write(str.encode("I'm a slow response LOL\n"))
    return

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

if __name__ == '__main__':
    server = ThreadingHTTPServer(('', args.port), Handler)
    server.serve_forever()