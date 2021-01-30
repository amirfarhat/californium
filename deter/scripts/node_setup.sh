#!/bin/bash

. /proj/MIT-DoS/exp/coap-setup/deps/californium/deter/scripts/config.sh

# Expect:
# Forked californium from source: https://github.com/amirfarhat/californium
if [ ! -d $CF_HOME ]
then
  echo "Base CF package not found"
  exit 1
fi

# Install utilities
sudo apt install -y iperf traceroute moreutils apache2

# Install Java: JDK, JRE
sudo apt install -y default-jdk default-jre