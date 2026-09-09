"""
maze.py — bikin peta labirin secara acak, dari 4 pola tembok (lihat config.py).
"""
import random
from config import TILE, PATTERNS, PATTERN_LETTERS


def gen_map(W, H):
    """Kembalikan (grid, tile_pattern).
    grid         -> list 2D karakter '0' (jalan) / '1' (tembok), ukuran H x W.
    tile_pattern -> list 2D huruf pola ('A'/'B'/'C'/'D') yang dipakai tiap tile,
                    dipakai nanti buat milih gambar tembok yang sesuai.
    """
    rnd = random.Random()
    g = [['1']*W for _ in range(H)]
    tiles_x = (W-1)//TILE
    tiles_y = (H-1)//TILE
    tile_pattern = [[None]*tiles_x for _ in range(tiles_y)]   # pola (huruf) tiap tile
    for ty in range(tiles_y):
        for tx in range(tiles_x):
            idx = rnd.randrange(4)
            pat = PATTERNS[idx]
            tile_pattern[ty][tx] = PATTERN_LETTERS[idx]   # simpan pola yang dipakai tile ini
            for lr in range(TILE):
                for lc in range(TILE):
                    gr = 1 + ty*TILE + lr
                    gc = 1 + tx*TILE + lc
                    if gr < H-1 and gc < W-1:
                        g[gr][gc] = pat[lr][lc]
    # bingkai terluar peta tetap tembok penuh
    for c in range(W):
        g[0][c] = '1'; g[H-1][c] = '1'
    for r in range(H):
        g[r][0] = '1'; g[r][W-1] = '1'
    return g, tile_pattern
