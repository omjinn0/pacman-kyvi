"""
main.py — VERSI KIVY (pengganti versi tkinter).
Nama file HARUS "main.py" karena itu yang dicari Buildozer nanti pas
compile ke APK.

Cara jalanin di Pydroid3: buka file ini, tekan Run (▶). Pydroid3 otomatis
deteksi Kivy dari baris "import kivy" di bawah dan jalanin dengan mode
yang benar.

Struktur folder yang dibutuhkan (sejajar semua):
    main.py
    config.py
    maze.py
    assets/
        pacman.png
        ghost.png
        wall_a.png, wall_b.png, wall_c.png, wall_d.png
        background.png
"""
import kivy
kivy.require('2.0.0')

import os, math, random

from kivy.config import Config
Config.set('graphics', 'fullscreen', 'auto')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, Ellipse, Line
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage
from kivy.clock import Clock

from config import (COLS, ROWS, N_GHOSTS, SHOW_PELLETS, DIRS, COLORS,
                     TILE, PATTERN_LETTERS, ASSET_DIR)
from maze import gen_map

# warna nama -> RGB 0..1 (dipakai buat nge-tint gambar hantu & warna oval fallback)
COLOR_RGB = {
    "red": (1, 0, 0), "pink": (1, .75, .8), "cyan": (0, 1, 1),
    "orange": (1, .65, 0), "purple": (.5, 0, .5), "lime": (0, 1, 0),
    "magenta": (1, 0, 1), "white": (1, 1, 1), "turquoise": (.25, .88, .82),
    "coral": (1, .5, .31), "violet": (.93, .51, .93), "gold": (1, .84, 0),
}


class GameWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.SW, self.SH = Window.width, Window.height
        self.CELL = max(50, min(100, self.SH // 10))
        self.rad = max(6, int(self.CELL * 0.45))

        self._load_assets()

        # posisi UI (joystick & tombol) pakai konvensi "atas ke bawah" biar
        # gampang dibandingkan sama versi tkinter sebelumnya
        self.JS = max(150, min(320, self.SH // 3))
        self.jc = (self.SW - self.JS // 2 - 14, int(self.SH * 0.72))
        MARGIN = 170
        self.shc = (MARGIN, int(self.SH * 0.72))
        self.shc2 = (MARGIN, int(self.SH * 0.72) - 170)

        self.knob = None
        self.drag_uid = None      # id sentuhan yang lagi pegang joystick
        self.shoot_uid = None
        self.rapid_uid = None
        self.rapid_held = False
        self.want = (0, 0)

        # label teks (Kivy nggambar teks lewat widget Label, bukan lewat canvas)
        self.score_label = Label(text="Score: 0", color=(1, 1, 1, 1),
                                  font_size='16sp', size=(200, 40),
                                  size_hint=(None, None), halign='left',
                                  valign='middle')
        self.score_label.text_size = self.score_label.size
        self.add_widget(self.score_label)

        self.btn_label = Label(text="TEMBAK", color=(1, 1, 1, 1),
                                font_size='13sp', bold=True,
                                size=(110, 40), size_hint=(None, None),
                                halign='center', valign='middle')
        self.btn_label.text_size = self.btn_label.size
        self.add_widget(self.btn_label)

        self.btn2_label = Label(text="BERUNTUN", color=(1, 1, 1, 1),
                                 font_size='11sp', bold=True,
                                 size=(110, 40), size_hint=(None, None),
                                 halign='center', valign='middle')
        self.btn2_label.text_size = self.btn2_label.size
        self.add_widget(self.btn2_label)

        self.end_label = None
        self._place_ui_labels()

        self.reset()
        Clock.schedule_interval(self.update, 1 / 30.)

    # ---------- muat gambar (opsional, sama seperti versi tkinter) ----------
    def _load_tex(self, fname):
        p = os.path.join(ASSET_DIR, fname)
        if os.path.isfile(p):
            try:
                return CoreImage(p).texture
            except Exception:
                return None
        return None

    def _load_assets(self):
        self.tex_pacman = self._load_tex("pacman.png")
        self.use_img_pacman = self.tex_pacman is not None

        self.tex_wall_generic = self._load_tex("wall.png")
        self.wall_tex = {}
        for letter in PATTERN_LETTERS:
            t = self._load_tex(f"wall_{letter.lower()}.png")
            if t: self.wall_tex[letter] = t
        self.use_img_wall = bool(self.wall_tex) or (self.tex_wall_generic is not None)

        self.tex_ghost = self._load_tex("ghost.png")
        self.use_img_ghost = self.tex_ghost is not None

        self.tex_background = self._load_tex("background.png")
        self.use_img_background = self.tex_background is not None

    def wall_texture(self, r, c):
        letter = None
        if not (r == 0 or r == ROWS - 1 or c == 0 or c == COLS - 1):
            ty, tx = (r - 1) // TILE, (c - 1) // TILE
            if 0 <= ty < len(self.TILE_PATTERN) and 0 <= tx < len(self.TILE_PATTERN[0]):
                letter = self.TILE_PATTERN[ty][tx]
        tex = self.wall_tex.get(letter) if letter else None
        return tex if tex is not None else self.tex_wall_generic

    # ---------- transformasi koordinat ----------
    # "topdown" = konvensi y makin besar makin ke bawah (kayak tkinter).
    # Kivy aslinya y makin besar makin ke ATAS, jadi perlu dibalik pas gambar.
    def u2s(self, x, y_topdown):
        return (x, self.SH - y_topdown)               # UI tetap (gak ikut kamera)

    def w2s(self, wx, wy):
        return (wx - self.camx, self.SH - (wy - self.camy))   # dunia (ikut kamera)

    def _place_ui_labels(self):
        sx, sy = self.u2s(140, 60)
        self.score_label.pos = (sx - 100, sy - 20)
        sx, sy = self.u2s(*self.shc)
        self.btn_label.pos = (sx - 55, sy - 20)
        sx, sy = self.u2s(*self.shc2)
        self.btn2_label.pos = (sx - 55, sy - 20)

    # ---------- sentuh (mendukung multi-sentuh asli Kivy) ----------
    def on_touch_down(self, touch):
        x, y = touch.x, self.SH - touch.y   # ke koordinat topdown
        if self.game_over:
            if self.rrect and self._in_restart(x, y):
                self.reset()
            return True
        if math.hypot(x - self.shc[0], y - self.shc[1]) < 80:
            self.shoot_uid = touch.uid
            self.shoot()
            touch.grab(self)
            return True
        if math.hypot(x - self.shc2[0], y - self.shc2[1]) < 80:
            self.rapid_uid = touch.uid
            self.rapid_held = True
            if self.ticks >= self.rapid_ready:
                self._spawn_bullet()
                self.rapid_ready = self.ticks + self.RAPID_COOLDOWN
            touch.grab(self)
            return True
        if math.hypot(x - self.jc[0], y - self.jc[1]) < self.JS // 2 + 20:
            self.drag_uid = touch.uid
            touch.grab(self)
            self._joystick_move(x, y)
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current is self and touch.uid == self.drag_uid:
            x, y = touch.x, self.SH - touch.y
            self._joystick_move(x, y)
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.uid == self.drag_uid:
            self.drag_uid = None
            self.knob = None
            self.pdir = (0, 0); self.want = (0, 0)
        if touch.uid == self.rapid_uid:
            self.rapid_uid = None
            self.rapid_held = False
        if touch.uid == self.shoot_uid:
            self.shoot_uid = None
        if touch.grab_current is self:
            touch.ungrab(self)
            return True
        return super().on_touch_up(touch)

    def _joystick_move(self, x, y):
        dx, dy = x - self.jc[0], y - self.jc[1]
        R = self.JS // 2 - 12
        m = math.hypot(dx, dy)
        if m > R:
            dx, dy = dx * R / m, dy * R / m
        self.knob = (self.jc[0] + dx, self.jc[1] + dy)
        if m > 6:
            if abs(dx) > abs(dy):
                self.want = (1, 0) if dx > 0 else (-1, 0)
            else:
                self.want = (0, 1) if dy > 0 else (0, -1)

    def _in_restart(self, x, y):
        x1, y1, x2, y2 = self.rrect
        return x1 <= x <= x2 and y1 <= y <= y2

    # ---------- tembak ----------
    def _spawn_bullet(self):
        d = self.pdir if self.pdir != (0, 0) else self.lastdir
        self.bullets.append({"x": self.px, "y": self.py, "d": d})

    def shoot(self):
        if self.game_over or self.ticks < self.shoot_ready:
            return
        self.shoot_ready = self.ticks + 30
        self._spawn_bullet()

    # ---------- logika ----------
    def reset(self):
        self.MAP, self.TILE_PATTERN = gen_map(COLS, ROWS)
        C = self.CELL
        self.ps = C * 0.22
        self.gs = C * 0.055
        self.px = C + C // 2; self.py = C + C // 2
        self.pdir = (0, 0); self.want = (0, 0); self.lastdir = (1, 0)
        self.score = 0; self.game_over = False
        self.ticks = 0; self.shoot_ready = 0
        self.rapid_ready = 0; self.RAPID_COOLDOWN = 8
        self.rapid_held = False
        self.bullets = []
        self.rrect = None
        if self.end_label:
            self.remove_widget(self.end_label)
            self.end_label = None

        self.pellets = {(c, r) for r in range(ROWS) for c in range(COLS)
                         if self.MAP[r][c] == '0'}

        rnd = random.Random()
        open_cells = [(c, r) for r in range(ROWS) for c in range(COLS)
                      if self.MAP[r][c] == '0' and (abs(c - 1) + abs(r - 1)) > 25]
        rnd.shuffle(open_cells)
        self.ghosts = []
        for i in range(min(N_GHOSTS, len(open_cells))):
            c, r = open_cells[i]
            self.ghosts.append({"col": c, "row": r, "c": COLORS[i % len(COLORS)],
                                 "mode": i % 2})
        for g in self.ghosts:
            g["x"] = g["col"] * C + C // 2; g["y"] = g["row"] * C + C // 2
            g["dir"] = (0, 0); g["alive"] = True; g["respawn"] = 0
            self.ghost_choose(g)

        self.camx = min(max(0, self.px - self.SW // 2), COLS * C - self.SW)
        self.camy = min(max(0, self.py - self.SH // 2), ROWS * C - self.SH)
        self.score_label.text = "Score: 0"

    def is_wall(self, x, y):
        c = int(x // self.CELL); r = int(y // self.CELL)
        if 0 <= r < ROWS and 0 <= c < COLS:
            return self.MAP[r][c] == '1'
        return True

    def can_move(self, x, y):
        r = self.rad - 1
        for dx in (-r, r):
            for dy in (-r, r):
                if self.is_wall(x + dx, y + dy):
                    return False
        return True

    def ghost_choose(self, g):
        opts = [d for d in DIRS if self.MAP[g["row"] + d[1]][g["col"] + d[0]] != '1']
        rev = (-g["dir"][0], -g["dir"][1])
        cands = [d for d in opts if d != rev] or opts
        if g.get("mode") and len(cands) > 1:
            best = random.choice(cands)
        else:
            pc, pr = int(self.px // self.CELL), int(self.py // self.CELL)
            best = min(cands, key=lambda d: (g["col"] + d[0] - pc) ** 2 + (g["row"] + d[1] - pr) ** 2)
        g["dir"] = best; g["tc"] = g["col"] + best[0]; g["tr"] = g["row"] + best[1]

    def ghost_step(self, g):
        C = self.CELL
        tx = g["tc"] * C + C // 2; ty = g["tr"] * C + C // 2
        dx, dy = tx - g["x"], ty - g["y"]; dist = math.hypot(dx, dy)
        if dist <= 0.001:
            g["col"], g["row"] = g["tc"], g["tr"]; self.ghost_choose(g); return
        if dist <= self.gs:
            g["x"], g["y"] = tx, ty; g["col"], g["row"] = g["tc"], g["tr"]
            self.ghost_choose(g)
        else:
            g["x"] += dx / dist * self.gs; g["y"] += dy / dist * self.gs

    def update(self, dt):
        if not self.game_over:
            self.ticks += 1
            self._step()
        self._redraw()

    def _step(self):
        C = self.CELL
        if self.rapid_held and self.ticks >= self.rapid_ready:
            self._spawn_bullet()
            self.rapid_ready = self.ticks + self.RAPID_COOLDOWN

        w = self.want
        if w != (0, 0): self.lastdir = w
        if w != (0, 0) and (self.pdir == (0, 0) or w == (-self.pdir[0], -self.pdir[1])):
            self.pdir = w
        elif w != (0, 0) and w != self.pdir:
            if w[0] != 0:
                lane = int(self.py // C) * C + C // 2
                if abs(self.py - lane) <= max(3, self.ps * 2.5) and \
                   self.can_move(self.px + w[0] * self.ps, lane):
                    self.py = lane; self.pdir = w
            else:
                lane = int(self.px // C) * C + C // 2
                if abs(self.px - lane) <= max(3, self.ps * 2.5) and \
                   self.can_move(lane, self.py + w[1] * self.ps):
                    self.px = lane; self.pdir = w

        nx = self.px + self.pdir[0] * self.ps; ny = self.py + self.pdir[1] * self.ps
        if self.can_move(nx, ny): self.px, self.py = nx, ny

        pc, prr = int(self.px // C), int(self.py // C)
        if (pc, prr) in self.pellets:
            self.pellets.discard((pc, prr))
            self.score += 10
            self.score_label.text = f"Score: {self.score}"
        if not self.pellets:
            self.end("YOU WIN!"); return

        self.camx = min(max(0, self.px - self.SW // 2), COLS * C - self.SW)
        self.camy = min(max(0, self.py - self.SH // 2), ROWS * C - self.SH)

        for b in list(self.bullets):
            b["x"] += b["d"][0] * C * 0.5
            b["y"] += b["d"][1] * C * 0.5
            if self.is_wall(b["x"], b["y"]):
                self.bullets.remove(b); continue
            for g in self.ghosts:
                if g["alive"] and math.hypot(b["x"] - g["x"], b["y"] - g["y"]) < C * 0.7:
                    g["alive"] = False
                    g["respawn"] = self.ticks + 240
                    if b in self.bullets: self.bullets.remove(b)
                    self.score += 50
                    self.score_label.text = f"Score: {self.score}"
                    break

        for g in self.ghosts:
            if not g["alive"] and self.ticks >= g["respawn"]:
                g["alive"] = True
                g["x"] = g["col"] * C + C // 2; g["y"] = g["row"] * C + C // 2
                g["dir"] = (0, 0); self.ghost_choose(g)

        for g in self.ghosts:
            if not g["alive"]: continue
            self.ghost_step(g)
            if math.hypot((self.px - g["x"]) / C, (self.py - g["y"]) / C) < 0.7:
                self.end("GAME OVER!"); return

    # ---------- gambar ulang tiap frame ----------
    def _redraw(self):
        self.canvas.clear()
        C = self.CELL
        with self.canvas:
            if self.use_img_background:
                Color(1, 1, 1, 1)
                Rectangle(texture=self.tex_background, pos=(0, 0), size=(self.SW, self.SH))

            c0 = max(0, int(self.camx // C)); c1 = min(COLS - 1, int((self.camx + self.SW) // C) + 1)
            r0 = max(0, int(self.camy // C)); r1 = min(ROWS - 1, int((self.camy + self.SH) // C) + 1)
            for r in range(r0, r1 + 1):
                for c in range(c0, c1 + 1):
                    if self.MAP[r][c] == '1':
                        sx, sy = self.w2s(c * C + C // 2, r * C + C // 2)
                        tex = self.wall_texture(r, c) if self.use_img_wall else None
                        if tex is not None:
                            Color(1, 1, 1, 1)
                            Rectangle(texture=tex, pos=(sx - C / 2, sy - C / 2), size=(C, C))
                        else:
                            Color(0, 0, 1, 1)
                            Line(rectangle=(sx - C / 2, sy - C / 2, C, C), width=1.5)

            if SHOW_PELLETS:
                pr = max(3, C // 6)
                Color(1, 1, 1, 1)
                for (c, r) in self.pellets:
                    if c0 <= c <= c1 and r0 <= r <= r1:
                        sx, sy = self.w2s(c * C + C // 2, r * C + C // 2)
                        Ellipse(pos=(sx - pr, sy - pr), size=(2 * pr, 2 * pr))

            br = max(4, C // 6)
            Color(0, 1, 0, 1)
            for b in self.bullets:
                sx, sy = self.w2s(b["x"], b["y"])
                Ellipse(pos=(sx - br, sy - br), size=(2 * br, 2 * br))

            r = self.rad
            for g in self.ghosts:
                if not g["alive"]: continue
                sx, sy = self.w2s(g["x"], g["y"])
                if self.use_img_ghost:
                    Color(*COLOR_RGB.get(g["c"], (1, 1, 1)), 1)
                    Rectangle(texture=self.tex_ghost, pos=(sx - r, sy - r), size=(2 * r, 2 * r))
                else:
                    Color(*COLOR_RGB.get(g["c"], (1, 1, 1)), 1)
                    Ellipse(pos=(sx - r, sy - r), size=(2 * r, 2 * r))

            sx, sy = self.w2s(self.px, self.py)
            if self.use_img_pacman:
                Color(1, 1, 1, 1)
                Rectangle(texture=self.tex_pacman, pos=(sx - r, sy - r), size=(2 * r, 2 * r))
            else:
                Color(1, 1, 0, 1)
                Ellipse(pos=(sx - r, sy - r), size=(2 * r, 2 * r))

            # --- UI: joystick & tombol tembak (posisi tetap, gak ikut kamera) ---
            jx, jy = self.u2s(*self.jc)
            R = self.JS // 2 - 12
            Color(0.5, 0.5, 0.5, 1)
            Line(circle=(jx, jy, R), width=2)
            kx, ky = self.u2s(*self.knob) if self.knob else (jx, jy)
            kr = self.JS // 6
            Color(1, 1, 0, 1)
            Ellipse(pos=(kx - kr, ky - kr), size=(2 * kr, 2 * kr))

            sx2, sy2 = self.u2s(*self.shc)
            if self.ticks >= self.shoot_ready:
                Color(1, 0, 0, 1)
            else:
                Color(0.5, 0.5, 0.5, 1)
            Ellipse(pos=(sx2 - 60, sy2 - 60), size=(120, 120))

            sx3, sy3 = self.u2s(*self.shc2)
            if self.rapid_held:
                Color(0.5, 0.5, 0.5, 1)
            else:
                Color(1, 0, 0, 1)
            Ellipse(pos=(sx3 - 60, sy3 - 60), size=(120, 120))

    def end(self, msg):
        self.game_over = True
        self.rapid_held = False
        cx, cy = self.SW // 2, self.SH // 2
        if not self.end_label:
            self.end_label = Label(text=f"{msg}\nScore: {self.score}\n\nTap buat mulai ulang",
                                    color=(1, 1, 0, 1), font_size='20sp', bold=True,
                                    size=(320, 160), size_hint=(None, None), halign='center',
                                    valign='middle')
            self.end_label.text_size = self.end_label.size
            self.add_widget(self.end_label)
        self.end_label.text = f"{msg}\nScore: {self.score}\n\nTap buat mulai ulang"
        sx, sy = self.u2s(cx, cy)
        self.end_label.pos = (sx - 160, sy - 80)
        self.rrect = (cx - 160, cy - 80, cx + 160, cy + 80)


class PacmanApp(App):
    def build(self):
        return GameWidget()


if __name__ == '__main__':
    PacmanApp().run()
