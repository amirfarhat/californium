#!/bin/bash

source /proj/MIT-DoS/exp/coap-setup/deps/californium/deter/scripts/config.sh

# Expect:
# Forked californium from source: https://github.com/amirfarhat/californium
if [ ! -d $CF_HOME ]
then
  echo "Base CF package not found"
  exit 1
fi

# Install utilities
sudo apt install -y iperf traceroute moreutils apache2 httpie

# Install Java: JDK, JRE
sudo apt install -y default-jdk default-jre

# Set small index.html as Apache homepage
sudo cp $DETER_HOME/utils/index.html /var/www/html/index.html

# # Increase the maximum length of processor input queues
# sudo sysctl -w net.core.netdev_max_backlog=$NETDEV_MAX_BACKLOG

# Set custom bashrc
sudo cp $DETER_HOME/utils/.bashrc ~/.bashrc
source ~/.bashrc