import sys

# Fetch src and dst from command line
src = None
dst = None
for i in range(1, len(sys.argv) - 1):
  if sys.argv[i].endswith("src"):
    src = sys.argv[i + 1]
  elif sys.argv[i].endswith("dst"):
    dst = sys.argv[i + 1]

with open('ips/%s.ips' % src, 'r') as f:
  for line in f:
    if line.startswith(dst):
      parts = line.split()
      _, dst_ip = parts
      print(dst_ip)