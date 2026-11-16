//! Where tapline keeps the player's things and finds the charts that come
//! with it.

use std::path::PathBuf;

/// The player's state folder: `$TAPLINE_STATE_DIR`, else
/// `$XDG_STATE_HOME/tapline`, else `~/.local/state/tapline` (Linux and the
/// BSDs), `~/Library/Application Support/tapline` (macOS) or
/// `%LOCALAPPDATA%\tapline` (Windows). None under `cfg(test)`, so tests never
/// touch a real one.
pub fn state_dir() -> Option<PathBuf> {
    let env = |k: &str| {
        std::env::var_os(k)
            .filter(|v| !v.is_empty())
            .map(PathBuf::from)
    };
    if let Some(dir) = env("TAPLINE_STATE_DIR") {
        return Some(dir);
    }
    if cfg!(test) {
        return None;
    }
    let base = env("XDG_STATE_HOME")
        .filter(|p| p.is_absolute())
        .or_else(|| {
            if cfg!(windows) {
                env("LOCALAPPDATA")
            } else if cfg!(target_os = "macos") {
                env("HOME").map(|h| h.join("Library/Application Support"))
            } else {
                env("HOME").map(|h| h.join(".local/state"))
            }
        })?;
    Some(base.join("tapline"))
}

/// The `songs` folder beside the program, where a packaged tapline keeps
/// the charts that come with it.
pub fn bundled_songs_dir() -> Option<PathBuf> {
    let exe = std::env::current_exe().ok()?;
    let exe = exe.canonicalize().unwrap_or(exe);
    let dir = exe.parent()?.join("songs");
    dir.is_dir().then_some(dir)
}

/// The player's own charts: `songs` in the state folder.
pub fn player_songs_dir() -> Option<PathBuf> {
    state_dir().map(|d| d.join("songs"))
}
