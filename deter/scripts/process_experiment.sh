#!/bin/bash

# Require that CF_HOME is set
if [[ -z "$CF_HOME" ]]; then
  echo "CF_HOME is empty or unset"  
  exit 1
fi

# Construct paths to data and scripts
DATA_DIR=$CF_HOME/deter/expdata/real/proxy
SCRIPTS_DIR=$CF_HOME/deter/scripts

# Accept experiment
ZIP_SUFFIX=".zip"
zipped_experiment_name=$1

# Construct full path to experiment by stripping zip suffix
_zipped_path="$DATA_DIR/$zipped_experiment_name"
exp_dir="${_zipped_path%$ZIP_SUFFIX}"

# Scp experiment data if not there already
if [[ ! -d $exp_dir ]]; then
  echo "${zipped_experiment_name%$ZIP_SUFFIX} not found. Fetching files..."
  REMOTE_EXP_DIR="/proj/MIT-DoS/exp/coap-setup/deps/californium/deter/expdata/real/proxy"
  scp -r amirf@users.deterlab.net:$REMOTE_EXP_DIR/$zipped_experiment_name $DATA_DIR
fi

# | Step 0 | Unzip experiment files
cd $DATA_DIR
unzip -n $zipped_experiment_name

# | Step 1 | Create (if not exists) processed CoAP tcpdumps
cd $SCRIPTS_DIR
pids=()
for D in $exp_dir/*/; do
  if [[ -d $D ]]; then
    echo "Processing CoAP tcpdumps in $D..."
    # Process attacker dump
    if [[ ! -f $D/processed_attacker_dump.out ]]; then
      if [[ -f $D/attacker_dump.pcap ]]; then
        (./process_tcpdump.sh $D/attacker_dump.pcap $D/processed_attacker_dump.out "attacker") &
        pids+=($!)
      fi
    fi
    # Process proxy dump
    if [[ ! -f $D/processed_proxy_dump.out ]]; then
      if [[ -f $D/proxy_dump.pcap ]]; then
        (./process_tcpdump.sh $D/proxy_dump.pcap $D/processed_proxy_dump.out "proxy") &
        pids+=($!)
      fi
    fi
    # Process receiver dump
    if [[ ! -f $D/processed_receiver_dump.out ]]; then
      if [[ -f $D/receiver_dump.pcap ]]; then
        (./process_tcpdump.sh $D/receiver_dump.pcap $D/processed_receiver_dump.out "receiver") &
        pids+=($!)
      fi
    fi
    # Process client dump
    if [[ ! -f $D/processed_client_dump.out ]]; then
      if [[ -f $D/client_dump.pcap ]]; then
        (./process_tcpdump.sh $D/client_dump.pcap $D/processed_client_dump.out "client") &
        pids+=($!)
      fi
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
    # # Assert presence of processed tcpdumps and proxy log
    # if [[ ! -f $D/processed_attacker_dump.out ]]; then
    #   echo "Could not find attacker dump in $D"
    #   exit 1
    # fi
    # if [[ ! -f $D/processed_proxy_dump.out ]]; then
    #   echo "Could not find proxy dump in $D"
    #   exit 1
    # fi
    # if [[ ! -f $D/processed_client_dump.out ]]; then
    #   echo "Could not find client dump in $D"
    #   exit 1
    # fi
    # if [[ ! -f $D/proxy.log ]]; then
    #   echo "Could not find proxy log in $D"
    #   exit 1
    # fi
    # Now issue tasks to process these
    if [[ ! -f $D/proxy_log_messages.csv ]]; then
      (python3 data_processor.py -t proxy_log -i $D/proxy.log -o $D/proxy_log_messages.csv) &
      pids+=($!)
    fi
    if [[ ! -f $D/proxy_messages.csv ]]; then
      if [[ -f $D/processed_proxy_dump.out ]]; then
        (python3 data_processor.py -t proxy_dump -i $D/processed_proxy_dump.out -o $D/proxy_messages.csv) &
        pids+=($!)
      fi
    fi
    if [[ ! -f $D/attacker_messages.csv ]]; then
      if [[ -f $D/processed_attacker_dump.out ]]; then
        (python3 data_processor.py -t attacker_dump -i $D/processed_attacker_dump.out -o $D/attacker_messages.csv) &
        pids+=($!)
      fi
    fi
    if [[ ! -f $D/receiver_messages.csv ]]; then
      if [[ -f $D/processed_receiver_dump.out ]]; then
        (python3 data_processor.py -t receiver_dump -i $D/processed_receiver_dump.out -o $D/receiver_messages.csv) &
        pids+=($!)
      fi
    fi
    if [[ ! -f $D/client_messages.csv ]]; then
      if [[ -f $D/processed_client_dump.out ]]; then
        (python3 data_processor.py -t client_dump -i $D/processed_client_dump.out -o $D/client_messages.csv) &
        pids+=($!)
      fi
    fi
  fi
done
# And wait for all processing to finish
for pid in "${pids[@]}"; do
  wait $pid
done
