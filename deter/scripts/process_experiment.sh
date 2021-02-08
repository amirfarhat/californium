#!/bin/bash

# Require that CF_HOME is set
if [[ -z "$CF_HOME" ]]; then
  echo "CF_HOME is empty or unset"  
  exit 1
fi

DATA_DIR=$CF_HOME/deter/expdata/real/proxy
SCRIPTS_DIR=$CF_HOME/deter/scripts

ZIP_SUFFIX=".zip"

zipped_experiment_name=$1

# | Step 0 | Unzip experiment files
cd $DATA_DIR
unzip -n $zipped_experiment_name

# Construct full path to experiment by stripping zip suffix
_zipped_path="$DATA_DIR/$zipped_experiment_name"
exp_dir="${_zipped_path%$ZIP_SUFFIX}"

# | Step 1 | Create (if not exists) processed CoAP tcpdumps
cd $SCRIPTS_DIR
pids=()
for D in $exp_dir/*/; do
  if [[ -d $D ]]; then
    echo "Processing CoAP tcpdumps in $D..."
    if [[ ! -f $D/processed_attacker_dump.out ]]; then
      (./process_tcpdump.sh $D/attacker_dump.pcap $D/processed_attacker_dump.out) &
      pids+=($!)
    fi
    if [[ ! -f $D/processed_proxy_dump.out ]]; then
      (./process_tcpdump.sh $D/proxy_dump.pcap $D/processed_proxy_dump.out) &
      pids+=($!)
    fi
  fi
done
# And wait for all processing to finish
for pid in "${pids[@]}"; do
  wait $pid
done

# | Step 2 | Process tcpdumps and proxy logs into csv
pids=()
for D in $exp_dir/*/; do
  if [[ -d $D ]]; then
    echo "Processing data into csvs in $D..."
    # Assert presence of processed tcpdumps and proxy log
    if [[ ! -f $D/processed_attacker_dump.out ]]; then
      echo "Could not find attacker dump in $D"
      exit 1
    fi
    if [[ ! -f $D/processed_proxy_dump.out ]]; then
      echo "Could not find proxy dump in $D"
      exit 1
    fi
    if [[ ! -f $D/proxy.log ]]; then
      echo "Could not find proxy log in $D"
      exit 1
    fi
    # Now issue tasks to process these
    if [[ ! -f $D/proxy_log_messages.csv ]]; then
      (python3 data_processor.py -t proxy_log -i $D/proxy.log -o $D/proxy_log_messages.csv) &
      pids+=($!)
    fi
    if [[ ! -f $D/proxy_messages.csv ]]; then
      (python3 data_processor.py -t proxy_dump -i $D/processed_proxy_dump.out -o $D/proxy_messages.csv) &
      pids+=($!)
    fi
    if [[ ! -f $D/attacker_messages.csv ]]; then
      (python3 data_processor.py -t attacker_dump -i $D/processed_attacker_dump.out -o $D/attacker_messages.csv) &
      pids+=($!)
    fi
  fi
done
# And wait for all processing to finish
for pid in "${pids[@]}"; do
  wait $pid
done
