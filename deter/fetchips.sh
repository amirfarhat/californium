#!/bin/bash

source /proj/MIT-DoS/exp/coap-setup/deps/californium/deter/scripts/config.sh

src=""
dst=""

if [[ ! -z $1 ]] && [[ ! -z $2 ]]; then
  # Case two inputs
  src=$1
  dst=$2
elif [[ ! -z $1 ]]; then
  # Case one input
  src=`hostname | awk -F. '{print $1}'` # src is current host
  dst=$1
else
  echo "Usage fetchips [dst] or fetchips [src] [dst]"
  exit 1
fi

cd $DETER_HOME
python fetchips_helper.py --src $src --dst $dst
