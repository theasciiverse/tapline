#!/usr/bin/env python3
"""bellbeat-charts.py RENDER OUT: keysound charts for tapline from a Bellbeat
song rendered with `bellbeat --render SONG RENDER` (and its WAVs encoded to
Ogg beside them, see bellbeat-charts.sh).

Writes OUT/<song>-4k.bmson and OUT/<song>-7k.bmson. The backing plays as
the chart's background music; every melody note is a note to hit, and its
keysound is that very note of the tune, so a hit plays the melody and a
miss leaves a hole in it. The 7-key chart is all of the melody; the 4-key
chart is the notes that start on a beat, and the others play themselves.
A note's lane follows the tune: higher notes to the right, and a step up or
down never stays in the lane before (Bellbeat's own rule). Notes of half a
bar or longer are long notes.

Each tone file sits in two sound channels that take turns, because tapline
cuts a keysound short when its channel sounds again; that way a note rings
on into the next one of the same pitch."""
import json, os, sys

render, out = sys.argv[1], sys.argv[2]
song = os.path.basename(os.path.normpath(render))
info = {}
for line in open(os.path.join(render, "song.txt")):
    k, _, v = line.rstrip("\n").partition(" ")
    if k != "section":
        info[k] = v
bpm, meter = float(info["bpm"]), int(info["meter"])
RES = 960
pulse = lambda secs: round(secs * bpm / 60 * RES)
step_secs = 60 / bpm / 4

notes = []
for line in open(os.path.join(render, "notes.tsv")):
    if line.startswith("#"):
        continue
    secs, midi, length, step, steps, name = line.rstrip("\n").split("\t")
    notes.append(dict(secs=float(secs), midi=int(midi), len=float(length),
                      step=int(step), steps=int(steps), tone=name.replace(".wav", ".ogg")))

def lanes(ns, n):
    if not ns:
        return []
    lo, hi = min(x["midi"] for x in ns), max(x["midi"] for x in ns)
    span = hi - lo + 1
    outl, prev = [], None
    for x in ns:
        lane = min(n - 1, int((x["midi"] - lo) / span * n))
        if prev:
            pm, pl = prev
            if x["midi"] > pm and lane <= pl:
                lane = pl + 1 if pl + 1 < n else max(pl - 1, 0)
            elif x["midi"] < pm and lane >= pl:
                lane = pl - 1 if pl > 0 else min(pl + 1, n - 1)
            elif x["midi"] == pm:
                lane = pl
        prev = (x["midi"], lane)
        outl.append(lane)
    return outl

def chart(keys, playable):
    mine = [x for x in notes if playable(x)]
    lane_of = dict(zip((id(x) for x in mine), lanes(mine, keys)))
    channels, turn = {}, {}
    for x in notes:
        t = turn.get(x["tone"], 0)
        turn[x["tone"]] = 1 - t
        ch = channels.setdefault((x["tone"], t), [])
        y = pulse(x["secs"])
        if id(x) in lane_of:
            hold = pulse(x["secs"] + x["len"] - step_secs) - y if x["steps"] >= 2 * meter else 0
            ch.append({"x": lane_of[id(x)] + 1, "y": y, "l": max(hold, 0), "c": False})
        else:
            ch.append({"x": 0, "y": y, "l": 0, "c": False})
    sound = [{"name": "backing.ogg", "notes": [{"x": 0, "y": 0, "l": 0, "c": False}]}]
    for (tone, _), ns in sorted(channels.items()):
        sound.append({"name": "tones/" + tone, "notes": ns})
    secs = float(info["secs"])
    nps = len(mine) / secs
    level = max(1, min(12, round(nps * 2.2)))
    name = "NORMAL" if keys == 4 else ("ANOTHER" if nps > 3.2 else "HYPER")
    return {
        "version": "1.0.0",
        "info": {
            "title": info["title"],
            "subtitle": "",
            "artist": "Bellbeat",
            "genre": "Bellbeat songs, Asciiverse",
            "mode_hint": "generic-%dkeys" % keys,
            "chart_name": name,
            "level": level,
            "init_bpm": bpm,
            "resolution": RES,
        },
        "sound_channels": sound,
    }, len(mine)

os.makedirs(out, exist_ok=True)
for keys, playable in ((4, lambda x: x["step"] % 4 == 0), (7, lambda x: True)):
    data, count = chart(keys, playable)
    path = os.path.join(out, "%s-%dk.bmson" % (song, keys))
    with open(path, "w") as f:
        json.dump(data, f, separators=(",", ":"))
    print("%s: %d of %d melody notes to play, level %d %s" % (
        os.path.basename(path), count, len(notes), data["info"]["level"], data["info"]["chart_name"]))
