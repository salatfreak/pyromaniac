#!/bin/bash

[[ -t 0 ]] && input='-it' || input='-i'

readonly DIR="$(realpath "$(dirname "$0")")"
exec podman run --rm "$input" \
  --security-opt "label=disable" \
  -v "$DIR/pyromaniac:/src/pyromaniac:ro" \
  -v "pyromaniac-cache:/data/cache" \
  -v "pyromaniac-secrets:/data/secrets" \
  -v ".:/spec:ro" \
  -p 8000:8000 \
  ghcr.io/salatfreak/pyromaniac "$@"
