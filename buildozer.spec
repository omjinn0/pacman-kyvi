[app]
title = Pacman
package.name = pacman
package.domain = org.bamst

# folder tempat main.py berada (. = folder ini sendiri)
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas
source.include_patterns = assets/*

version = 1.0
requirements = python3,kivy

# --- ICON APLIKASI ---
# taruh file gambar icon (disarankan PNG persegi, contoh 512x512) di folder
# ini (sejajar sama main.py), lalu tulis nama filenya di sini.
icon.filename = %(source.dir)s/icon.png

# (opsional) gambar splash screen yang muncul sesaat pas app baru dibuka
# presplash.filename = %(source.dir)s/presplash.png

orientation = portrait
fullscreen = 1

# izin akses yang dibutuhkan di Android
android.permissions = INTERNET

[buildozer]
log_level = 2
warn_on_root = 1
