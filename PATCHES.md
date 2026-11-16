# Changes from upstream

This is the Asciiverse packaging of [tapline](https://github.com/unhappychoice/tapline)
by unhappychoice (Yuji Ueki), MIT (`LICENSE`): a rhythm game in the
terminal that plays BMS and bmson charts with their keysounds and
background music. Upstream is the `upstream` remote; this build is
upstream's `main` at `d100b73` (2026-11-16), version 0.1.0. The
`asciiverse` branch carries the changes below, one commit each. The code
changes are written so they could go upstream as they are.

## Code

- **Charts found wherever tapline is started from** (`3fdf593`). Without
  `--dir` or `TAPLINE_SONGS_DIR`, the selector lists, together, the
  charts in a `songs` folder beside the program, the player's own in
  `songs` in the state folder, and the first of `./songs`,
  `./tests/fixtures` and `~/.tapline/songs` as before. Upstream looked only
  at the first of those it found, relative to the current folder.
  (`src/paths.rs`, `src/cli.rs`, `src/select.rs`)
- **Results in the state folder** (`8b954ca`). `results.json` lives in
  `$XDG_STATE_HOME/tapline`, else `~/.local/state/tapline` (Linux and the
  BSDs), `~/Library/Application Support/tapline` (macOS) or
  `%LOCALAPPDATA%\tapline` (Windows). `TAPLINE_STATE_DIR` sets the folder,
  `TAPLINE_DATA_DIR` still sets the one for `results.json`. A
  `results.json` in upstream's folder (`$XDG_DATA_HOME/tapline`) is copied
  over once. (`src/results.rs`)
- **Session logging** (`518c162`) with `log` and `env_logger`:
  `RUST_LOG=debug tapline 2>tapline.log`. Every terminal event as it is
  read, in the selector and in play (with the play clock); the chart
  chosen, countdown, play, quitting, completion and the final tally; a
  snapshot every half second (position, score, combo, judgements, gauge,
  keys held). Without `RUST_LOG`, only errors. (`src/main.rs`,
  `src/select.rs`, `src/runtime.rs`)
- **No sound from tests; `TAPLINE_NO_AUDIO`** (`a802312`). Unit tests never
  open a sound device, and the test processes that load samples set
  `TAPLINE_NO_AUDIO`, which keeps tapline from opening one at all (the
  selector's previews included). (`src/audio.rs`, `tests/audio_bank.rs`)
- **`--autoplay`** (`b9658cd`): a chart plays itself, every note hit as it
  reaches the line with its keysound, long notes held to their end;
  results are shown, not saved. Used for the catalog preview.
  (`src/cli.rs`, `src/runtime.rs`)
- **Each frame drawn whole** (`f4c5f72`). The play screen drew on top of
  the last frame in its off-screen model, so moving text left letters
  behind: once PERFECT reached 100, the centred counters shifted and read
  GGREAT, GGOOD and MMISS. The model is blanked before each frame; only
  changed cells are still sent. (`src/runtime.rs`)
- **Selector rows fit the screen** (`db3dbe4`). A row starts two columns in
  but was cut at the full width, so a long one wrapped onto the next line;
  it is now cut to fit. (`src/select.rs`)

## Music

- **Keysound charts of eight Bellbeat songs** (`c4315f4`), in
  `songs/bellbeat`: Hello, World; Segfault March; Waltz for a Spinning
  Disk; Carriage Return; Escape Sequence; Kernel Panic; Null Pointer
  Samba; SIGTERM. Bellbeat is the Asciiverse's own rhythm game
  ([theasciiverse/bellbeat](https://github.com/theasciiverse/bellbeat),
  MIT) and every song in it was written for it. Its synth renders each
  song (`bellbeat --render`, added for this): the backing becomes the
  chart's background music and each melody note its own keysound, so
  every hit plays that note of the tune. Per song, a 4-key chart (the
  notes on the beat to play, the rest playing itself) and a 7-key chart
  (the whole melody); lanes follow the melody's shape, higher notes to the
  right. Ogg Vorbis, 9.9 MB in all. Made by `asciiverse/bellbeat-charts.sh`
  from a Bellbeat checkout (with `asciiverse/bellbeat-charts.py`);
  `tests/bellbeat_charts.rs` checks that every chart loads and every sound
  it names is there, and the scan test in `tests/bms_charts.rs` counts the
  eight hand-written charts at the top of `songs/` only.
- tapline's own eight charts in `songs/` ship unchanged.

## Packaging (new files)

- `.github/workflows/asciiverse-release.yml`: av archives for Linux
  (glibc, x86-64 and ARM64, built on Ubuntu 22.04), macOS (Apple silicon
  and Intel) and Windows (x86-64 and ARM64), each with the binary and the
  `songs` folder beside it, plus SHA256SUMS. Rust pinned to 1.93.1. Linux
  is not static musl: sound goes out through cpal and ALSA, linked
  dynamically, so the binary needs `libasound2`. Upstream's `ci.yml` runs
  on its `main` only and is left as it is.
- `asciiverse/record-preview.sh`: the catalog preview, Null Pointer Samba
  on 7 keys played by `--autoplay`, recorded with hub's `castrec.py`.
- `asciiverse/tapline.toml`, `asciiverse/tapline.md`,
  `asciiverse/tapline.cast`: the catalog manifest, store page and
  preview, drafts for hub.
