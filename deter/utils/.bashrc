alias cl='clear'

function hg () {
  eval "history | grep $@"
}

export -f hg