#!/bin/bash

# Require that CF_HOME is set
if [[ -z "$CF_HOME" ]]; then
  echo "CF_HOME is empty or unset"  
  exit 1
fi

DATA_DIR=$CF_HOME/deter/expdata/real/proxy
SCRIPTS_DIR=$CF_HOME/deter/scripts

experiment_name=$1

# Construct full path to experiment directory
exp_dir="$DATA_DIR/$experiment_name"

cd $SCRIPTS_DIR

for D in $exp_dir/*/; do
  if [[ -d $D ]]; then
    echo "Looking for processed files in $D..."

    # Processed dumps
    rm $D/*_dump.out
    
    # Csvs
    rm $D/*_messages.csv
  fi
done