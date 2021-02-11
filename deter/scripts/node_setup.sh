#!/bin/bash

source /proj/MIT-DoS/exp/coap-setup/deps/californium/deter/scripts/config.sh

# Fix weird bug where we can't apt install
sudo dpkg --configure -a

# Expect:
# Forked californium from source: https://github.com/amirfarhat/californium
if [[ ! -d $CF_HOME ]]; then
  echo "Base CF package not found"
  exit 1
fi

# Get Java async profiler
if [[ ! -d $UTILS_HOME/$PROFILER_DIR_NAME  ]]; then
  cd $UTILS_HOME
  wget $PROFILE_BINARY_URL
  tar xzvf $PROFILE_BINARY_NAME
fi

# Install utilities
sudo apt install -y iperf traceroute moreutils apache2 httpie linux-tools-generic linux-cloud-tools-generic linux-tools-4.15.0-112-generic linux-cloud-tools-4.15.0-112-generic openjdk-11-dbg

# Install Java: JDK, JRE
sudo apt install -y default-jdk default-jre

# Set small index.html as Apache homepage
sudo cp $UTILS_HOME/index.html /var/www/html/index.html

# Set custom bashrc
sudo cp $UTILS_HOME/.bashrc ~/.bashrc
source ~/.bashrc