#!/bin/bash

source /proj/MIT-DoS/exp/coap-setup/deps/californium/deter/scripts/config.sh

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
sudo apt install -y openjdk-11-jdk openjdk-11-jre

# Configure Apache
yes | sudo cp $UTILS_HOME/index.html /var/www/html/index.html
yes | sudo cp $UTILS_HOME/apache2.conf /etc/apache2/apache2.conf
yes | sudo cp $UTILS_HOME/.htaccess /var/www/html/.htaccess
sudo a2enmod rewrite

# Set custom bashrc
yes | sudo cp $UTILS_HOME/.bashrc ~/.bashrc
source ~/.bashrc