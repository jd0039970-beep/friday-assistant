// F.R.I.D.A.Y Tauri shell
// Tab = push-to-talk, Esc = silence / interrupt

#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    tauri::Builder::default()
        .setup(|app| {
            // Global hotkeys are registered here when the full Tauri global-shortcut
            // plugin is enabled. Until then the HUD listens for Tab/Esc while focused.
            let _ = app;
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running F.R.I.D.A.Y");
}
