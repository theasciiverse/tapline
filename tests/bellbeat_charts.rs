//! The keysound charts of Bellbeat songs in songs/bellbeat (made by
//! asciiverse/bellbeat-charts.sh): each song has a 4-key and a 7-key
//! chart, every sound they name is there, the backing plays as background
//! music from the start, and every melody note sounds once, as a note to
//! hit or by itself.

use std::path::Path;

#[test]
fn every_bellbeat_chart_loads_with_all_its_sounds() {
    let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("songs/bellbeat");
    let mut songs = 0;
    for entry in std::fs::read_dir(&root).unwrap() {
        let dir = entry.unwrap().path();
        if !dir.is_dir() {
            continue;
        }
        let song = dir.file_name().unwrap().to_string_lossy().into_owned();
        songs += 1;
        let mut melody = None;
        for keys in [4usize, 7] {
            let path = dir.join(format!("{song}-{keys}k.bmson"));
            let chart = tapline::bmson::load(&path, 0.0).unwrap();
            assert_eq!(chart.lane_count, keys, "{}", path.display());
            assert!(!chart.notes.is_empty(), "{}", path.display());
            for p in chart.wav_paths.values() {
                assert!(p.is_file(), "{} names {}", path.display(), p.display());
            }
            let backing = chart
                .bgm
                .iter()
                .filter(|e| chart.wav_paths[&e.keysound].ends_with("backing.ogg"))
                .count();
            assert_eq!(backing, 1, "{}", path.display());
            assert!(chart.bgm.iter().any(|e| e.time_ms == 0.0));
            let sounding = chart.notes.len() + chart.bgm.len() - 1;
            assert!(chart.notes.iter().all(|n| n.keysound.is_some()));
            match melody {
                None => melody = Some(sounding),
                Some(m) => assert_eq!(m, sounding, "{song}: both charts sound the whole melody"),
            }
        }
    }
    assert!(songs >= 6, "{songs} songs");
}
