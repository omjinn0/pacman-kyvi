"""
config.py — SEMUA PENGATURAN GAME ADA DI SINI.
File ini yang paling sering perlu kamu ubah (ukuran map, jumlah hantu,
warna, dll). File lain (game.py, assets.py, maze.py) jarang perlu disentuh.
"""
import os

# --- lokasi folder gambar ---
# taruh file gambar kamu di folder "assets" (satu folder sama file main.py):
#   assets/pacman.png     -> gambar Pac-Man
#   assets/ghost.png      -> gambar hantu (akan diberi tint warna beda tiap hantu)
#   assets/wall_a.png     -> tekstur tembok untuk pola A (blok padat)
#   assets/wall_b.png     -> tekstur tembok untuk pola B (silang/plus)
#   assets/wall_c.png     -> tekstur tembok untuk pola C (zigzag)
#   assets/wall_d.png     -> tekstur tembok untuk pola D (pilar)
#   assets/wall.png       -> tekstur cadangan, dipakai kalau wall_x.png di atas gak ada
#   assets/background.png -> gambar latar belakang, meregangkan penuh 1 layar
# PNG transparan (background bening) hasilnya paling bagus. Kalau file tidak
# ada / Pillow tidak terpasang, game otomatis balik pakai bentuk lama (oval/kotak).
ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

# --- ukuran map & jumlah musuh ---
COLS = 241; ROWS = 121   # ukuran peta (kolom x baris). Harus kelipatan TILE + 1
N_GHOSTS = 12             # jumlah hantu

# --- tampilan ---
SHOW_PELLETS = False   # ganti True kalau mau titik-titik pellet putih muncul lagi
PUTAR = 90              # ganti ke 270 kalau layar/gambar kebalik pas HP rotasi

# --- kontrol arah ---
DIRS = [(1,0),(-1,0),(0,1),(0,-1)]

# --- warna hantu (dipakai kalau gambar ghost.png gak ada, atau buat tint) ---
COLORS = ["red","pink","cyan","orange","purple","lime",
          "magenta","white","turquoise","coral","violet","gold"]

# --- 4 kombinasi blok tembok (tile 10x10). '0' = jalan, '1' = tembok. ---
# Baris/kolom terluar tiap tile SELALU '0' supaya antar tile otomatis nyambung.
TILE = 10
PATTERN_A = [   # blok padat
    "0000000000",
    "0111111110",
    "0111111110",
    "0111111110",
    "0111111110",
    "0111111110",
    "0111111110",
    "0111111110",
    "0111111110",
    "0000000000",
]
PATTERN_B = [   # bentuk plus/silang (4 blok di pojok)
    "0000000000",
    "0111001110",
    "0111001110",
    "0111001110",
    "0000000000",
    "0000000000",
    "0111001110",
    "0111001110",
    "0111001110",
    "0000000000",
]
PATTERN_C = [   # zigzag/S
    "0000000000",
    "0111111000",
    "0111111000",
    "0000000000",
    "0000000000",
    "0000000000",
    "0001111110",
    "0001111110",
    "0000000000",
    "0000000000",
]
PATTERN_D = [   # empat pilar kecil
    "0000000000",
    "0000000000",
    "0011001100",
    "0011001100",
    "0000000000",
    "0000000000",
    "0011001100",
    "0011001100",
    "0000000000",
    "0000000000",
]
PATTERNS = [PATTERN_A, PATTERN_B, PATTERN_C, PATTERN_D]
PATTERN_LETTERS = ['A', 'B', 'C', 'D']
