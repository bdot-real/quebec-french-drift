#!/bin/sh
# Import a GGUF model from HuggingFace into Ollama.
#
#   scripts/fetch_hf_gguf.sh <local-name> <huggingface-resolve-url>
#
# Why not `ollama pull hf.co/<repo>`: that path stalls at ~99.9% on some
# setups. Fetching the file directly and importing it with a Modelfile is
# slower to type and more reliable.
#
# The size check is not ceremony. A truncated or doubly-written GGUF still
# carries a valid "GGUF" magic in its first four bytes, so the header tells you
# nothing -- an earlier fetch here produced a file 540 MB too large (two curls
# writing one path, one of them resuming) and looked fine by every cheap test.
# Compare against Content-Length, or you will benchmark a corrupt model.
set -e

NAME="$1"
URL="$2"
DIR="${GGUF_DIR:-$HOME/.cache/qfdrift-gguf}"

if [ -z "$NAME" ] || [ -z "$URL" ]; then
  echo "usage: $0 <local-name> <huggingface-resolve-url>" >&2
  exit 2
fi

mkdir -p "$DIR"
FILE="$DIR/$NAME.gguf"

EXPECT=$(curl -sIL "$URL" | awk 'tolower($1) ~ /^content-length:/ {n=$2} END {gsub(/\r/,"",n); print n}')
if [ -z "$EXPECT" ]; then
  echo "could not determine the expected size from $URL" >&2
  exit 1
fi

if [ -s "$FILE" ] && [ "$(stat -f%z "$FILE" 2>/dev/null || stat -c%s "$FILE")" = "$EXPECT" ]; then
  echo "already have $NAME ($EXPECT bytes)"
else
  echo "fetching $NAME ($EXPECT bytes)"
  # No -C: resuming onto a file another process is writing is exactly how the
  # silent corruption happened. Always start clean.
  curl -fL --progress-bar --retry 5 --retry-delay 3 -o "$FILE" "$URL"
  GOT=$(stat -f%z "$FILE" 2>/dev/null || stat -c%s "$FILE")
  if [ "$GOT" != "$EXPECT" ]; then
    echo "size mismatch for $NAME: got $GOT, expected $EXPECT -- refusing to import" >&2
    exit 1
  fi
fi

printf 'FROM %s\n' "$FILE" > "$DIR/$NAME.Modelfile"
ollama create "$NAME" -f "$DIR/$NAME.Modelfile"
echo "imported as '$NAME' -- test it before benchmarking:"
echo "  ollama run $NAME 'Réécris en français : Le stationnement est ouvert.'"
