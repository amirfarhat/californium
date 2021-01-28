
source ./config.sh

# Options
while getopts ":v" opt; do
  case "$opt" in
    "v") _V=1;;
  esac
done

# Debug printer
function log () {
  if [[ $_V -eq 1 ]]; then
    printf "$@"
  fi
}

# Attacker
log "[SETUP] Starting attackers...\n"
ssh $RUN_USER@$ATTACKER_NAME "$SCRIPTS_HOME/start_attacker.sh -v"
