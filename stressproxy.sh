# Number of parallel requests to make
N=$1

# HTTP URL to access
httpdst=$2

proxycmd="java -jar demo-apps/run/cf-proxy2-3.0.0-SNAPSHOT.jar ExampleProxy2CoapClient $httpdst"

mkdir -p outs
rm outs/*

# Execute N requests via the proxy asynchronously
for ((i = 0 ; i < $N ; i++)); do
  eval "$proxycmd/$i" > "outs/out$i.txt" &
  pids[${i}]=$!
  echo "Sent Req ${i}"
done

# Wait on all requests to complete
echo "Waiting for responses"
for pid in ${pids[*]}; do
  wait $pid
done