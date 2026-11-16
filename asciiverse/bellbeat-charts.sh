#!/bin/sh
# Makes the keysound charts of Bellbeat songs that come with tapline in
# the Asciiverse: songs from Bellbeat, the Asciiverse's own rhythm game, all
# written for it and rendered by its own synth (`bellbeat --render`). For
# each song, songs/bellbeat/<song>/ gets the backing and every melody note
# as Ogg Vorbis, and a 4-key and a 7-key chart (bellbeat-charts.py).
#   asciiverse/bellbeat-charts.sh BELLBEAT_CHECKOUT
# Needs a Bellbeat checkout with --render (theasciiverse/bellbeat, ce45503
# or later), cargo, Python 3 and ffmpeg with libvorbis.
set -eu
SONGS="hello-world segfault-march waltz-for-a-spinning-disk carriage-return escape-sequence kernel-panic null-pointer-samba sigterm"
bellbeat=$(cd "$1" && pwd)
here=$(cd "$(dirname "$0")/.." && pwd)
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
(cd "$bellbeat" && cargo build --release -q)
rm -rf "$here/songs/bellbeat"
for s in $SONGS; do
  "$bellbeat/target/release/bellbeat" --render "$s" "$work/$s"
  dest="$here/songs/bellbeat/$s"
  mkdir -p "$dest/tones"
  ffmpeg -loglevel error -y -i "$work/$s/backing.wav" -c:a libvorbis -q:a 4 "$dest/backing.ogg"
  for t in "$work/$s/tones/"*.wav; do
    ffmpeg -loglevel error -y -i "$t" -c:a libvorbis -q:a 4 "$dest/tones/$(basename "$t" .wav).ogg"
  done
  python3 -I "$here/asciiverse/bellbeat-charts.py" "$work/$s" "$dest"
done
du -sh "$here/songs/bellbeat"
