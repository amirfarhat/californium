#!/bin/bash

# Require that CF_HOME is set
if [[ -z "$CF_HOME" ]]; then
  echo "CF_HOME is empty or unset"  
  exit 1
fi

SCRIPTS_DIR=$CF_HOME/deter/scripts
cd $SCRIPTS_DIR

exp_dir=$1

for D in $exp_dir/*/; do
  if [[ -d $D ]]; then
    echo "Looking for processed files in $D..."

    # Dumps
    if [[ -f $D/processed_attacker_dump.out ]]; then
      echo "Removing processed_attacker_dump.out..."
      rm $D/processed_attacker_dump.out
    fi
    if [[ -f $D/processed_proxy_dump.out ]]; then
      echo "Removing processed_proxy_dump.out..."
      rm $D/processed_proxy_dump.out
    fi
    
    # Csvs
    if [[ -f $D/attacker_messages.csv ]]; then
      echo "Removing attacker_messages.csv..."
      rm $D/attacker_messages.csv
    fi
    if [[ -f $D/proxy_messages.csv ]]; then
      echo "Removing proxy_messages.csv..."
      rm $D/proxy_messages.csv
    fi
    if [[ -f $D/proxy_log_messages.csv ]]; then
      echo "Removing proxy_log_messages.csv..."
      rm $D/proxy_log_messages.csv
    fi
  fi
done