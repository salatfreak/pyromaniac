#!/bin/bash

# extract server parameters from arguments
serve=false port=8000 cache=true debug=false
declare -a args=("$@")
for (( i = 0; i < $#; ++i )); do
  case "${args[i]}" in
    -- | -p | --pretty | -s | --strict | --help \
      | --iso-arch=* | --iso-net=* | --iso-disk=* | --auth=* \
      | --iso-raw-force | --iso-raw-help | --iso-raw-*=* ) ;;
    --iso-arch | --iso-net | --iso-disk | --auth | --iso-raw-* ) let ++i;;
    --serve ) serve=true;;
    --iso ) serve=false;;
    --address | --address=*)
      [[ "${args[i]}" == *=* ]] && addr="${args[i]#*=}" || addr="${args[++i]}"
      [[ ! "${addr%/}" =~ :([0-9]+)$ ]] || port="${BASH_REMATCH[1]}"
      ;;
    --no-cache ) cache=false; unset args[i];;
    --debug ) debug=true; unset args[i];;
    * ) break;;
  esac
  [[ "${args[i]}" != '--' ]] || break
done

# collect extra arguments
declare -a params=()
if $cache; then
  params+=(--volume 'pyromaniac-cache:/data/cache')
  params+=(--volume 'pyromaniac-secrets:/data/secrets')
fi
if $debug; then
  dir="$(dirname "$(realpath "$0")")"
  params+=(--volume "$dir/pyromaniac:/src/pyromaniac:ro")
  params+=(--volume "$dir/stdlib:/usr/local/lib/pyromaniac:ro")
fi
if [[ -t 0 ]]; then params+=(--tty); fi
if $serve; then params+=(--publish "$port:8000"); fi

# run pyromaniac using podman
exec podman run \
  --rm --interactive --security-opt 'label=disable' \
  --volume '.:/spec:ro' \
  "${params[@]}" \
  ghcr.io/salatfreak/pyromaniac:0.3.0 "${args[@]}"
