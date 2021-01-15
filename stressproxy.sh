#!/usr/bin/env bash

# Number of parallel requests to make
N=$1

# HTTP URL to access
httpdst=$2

# CoAP endpoint of proxy without port
proxyendpoint=$3

# Name of output directory
outdir=$4

# Flag to wait for responses
awaitresponses=$5

mkdir -p $outdir
rm $outdir/*

proxycmdprefix="java -jar demo-apps/run/cf-proxy2-3.0.0-SNAPSHOT.jar ExampleProxy2CoapClient"

# Execute N requests via the proxy asynchronously
for ((i = 0 ; i < $N ; i++)); do
  proxycmd="$proxycmdprefix $httpdst/$i $proxyendpoint"
  eval "$proxycmd" > "$outdir/out$i.txt" &
  pids[${i}]=$!
  echo "Sent Req ${i}"
done

# Wait on all requests to complete
if [ ! -z "$awaitresponses" ]; then
  echo "Waiting for responses"
  for pid in ${pids[*]}; do
    wait $pid
  done
fi