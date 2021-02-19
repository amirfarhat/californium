#!/bin/bash

# Require that CF_HOME is set
if [[ -z "$CF_HOME" ]]; then
  echo "CF_HOME is empty or unset"  
  exit 1
fi

# Construct paths to data and scripts
DATA_DIR=$CF_HOME/deter/expdata/real/proxy
SCRIPTS_DIR=$CF_HOME/deter/scripts

# Construct full path to experiment by stripping zip suffix
zipped_experiment_name=$1
proper_experiment_name="${zipped_experiment_name%.zip}"
exp_dir="$DATA_DIR/$proper_experiment_name"

echo "$proper_experiment_name"
echo "$exp_dir"

# Scp experiment data if not there already
if [[ ! -d $exp_dir ]]; then
  echo "${zipped_experiment_name%$ZIP_SUFFIX} not found. Fetching files..."
  REMOTE_EXP_DIR="/proj/MIT-DoS/exp/coap-setup/deps/californium/deter/expdata/real/proxy"
  scp -r amirf@users.deterlab.net:$REMOTE_EXP_DIR/$zipped_experiment_name $DATA_DIR
fi

# | Step 0 | Unzip experiment files
cd $DATA_DIR
unzip -n $zipped_experiment_name

# | Step 1 | Parse (if not exists) tcpdumps
cd $SCRIPTS_DIR
pids=()
for D in $exp_dir/*; do
  if [[ -d $D ]]; then
    echo "Parsing tcpdumps in `basename $D`..."
    # Process (if not already processed) the tcpdumps
    for dump_file in $D/*_dump.pcap; do
      processed_dump_file="$dump_file.out"
      if [[ ! -f $processed_dump_file ]]; then
        echo "Processing `basename $dump_file`..."
        (./process_tcpdump.sh $dump_file $processed_dump_file) &
        pids+=($!)
      fi
    done
  fi
done
# And wait for all processing to finish
for pid in "${pids[@]}"; do
  wait $pid
done

# | Step 2 | Write tcpdumps as csv
pids=()
for D in $exp_dir/*; do
  if [[ -d $D ]]; then
    echo "Processing tcpdumps in `basename $D`..."
    # Collect input files for processing
    infiles=""
    nice_infiles=""
    for processed_dump_file in $D/*_dump.pcap.out; do
      infiles+="$processed_dump_file;"
      nice_infiles+="`basename $processed_dump_file`,"
    done
    # Process all input files into one file
    outfile="$D/$proper_experiment_name.csv"
    (python3 data_processor.py -i $infiles -o $outfile) &
    pids+=($!)
  fi
done
# And wait for all processing to finish
for pid in "${pids[@]}"; do
  wait $pid
done
