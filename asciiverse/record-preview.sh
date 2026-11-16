#!/bin/sh
# Records the 100x30 catalog preview, asciiverse/tapline.cast
# (hub/RECORDING.md), with hub's castrec.py: Null Pointer Samba, one of the
# Bellbeat keysound charts that come with this build, on 7 keys, played
# start to finish by --autoplay with no sound device opened
# (TAPLINE_NO_AUDIO), then the result screen and out.
# Needs Python 3 and a hub checkout beside games/.
#   asciiverse/record-preview.sh
set -eu
cd "$(dirname "$0")/.."
here=$(pwd)
castrec=$(cd ../../hub/tools && pwd)/castrec.py
cargo build --release -q
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cp target/release/tapline "$tmp/" && cp -r songs "$tmp/songs"
(cd "$tmp" && PATH="$tmp:$PATH" HOME="$tmp" XDG_STATE_HOME="$tmp/state" TAPLINE_NO_AUDIO=1 \
  python3 "$castrec" "$here/asciiverse/tapline.cast" . "w57.6;kenter;w0.5" \
  -- tapline --file songs/bellbeat/null-pointer-samba/null-pointer-samba-7k.bmson --autoplay --countdown-ms 1000)
ls -l asciiverse/tapline.cast
