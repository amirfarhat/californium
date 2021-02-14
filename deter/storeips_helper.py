from pprint import pprint

fname = "exp_links_info.txt"
link_map_nodes = dict()
node_map_links = dict()

with open(fname, 'r') as f:
  capture = False
  for line in f:
    # Start recording
    if line.startswith("Virtual Lan/Link Info"):
      capture = True

    # Stop recording
    if line.startswith("Physical Lan/Link Mapping"):
      capture = False

    # Capture link information
    if capture and line.startswith("Link-"):
      parts = line.split()

      link = parts[0]
      name = parts[1][:parts[1].index(':')]
      ip = parts[2]

      link_map_nodes.setdefault(link, list()).append((name, ip))
      node_map_links.setdefault(name, list()).append(link)

node_names = set(node_map_links.keys())

# Record context-dependent IP addresses
records = dict()
for n1 in node_names:
  records.setdefault(n1, [])
  for link in node_map_links[n1]:
    for n2_ip_tuple in link_map_nodes[link]:
      n2, ip = n2_ip_tuple
      if n2 == n1:
        continue
      records[n1].append(n2_ip_tuple)

pprint(records)

# Write this information in separate files
for n1, other_nodes in sorted(records.items()):
  with open('ips/%s.ips' % n1, 'w') as f:
    for n2, ip in other_nodes:
      f.write("%s %s\n" % (n2, ip))