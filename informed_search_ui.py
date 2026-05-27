import copy, heapq, tkinter as tk
from tkinter import ttk, messagebox
import threading, time, random

# ══════════════════════════════════════════════════════
#  THUẬT TOÁN  –  Greedy & A*
# ══════════════════════════════════════════════════════

def state_to_tuple(s): return tuple(tuple(r) for r in s)

def get_blank(s):
    for i in range(3):
        for j in range(3):
            if s[i][j] == 0: return i, j

def get_actions(s):
    r, c = get_blank(s); acts = []
    if r > 0: acts.append('U')
    if r < 2: acts.append('D')
    if c > 0: acts.append('L')
    if c < 2: acts.append('R')
    return acts

def do_move(s, a):
    r, c = get_blank(s)
    dr = {'U': -1, 'D': 1, 'L': 0, 'R': 0}[a]
    dc = {'U': 0,  'D': 0, 'L': -1, 'R': 1}[a]
    ns = copy.deepcopy(s)
    ns[r][c], ns[r+dr][c+dc] = ns[r+dr][c+dc], ns[r][c]
    return ns

def h_misplaced(s, g):
    return sum(1 for i in range(3) for j in range(3)
               if s[i][j] != 0 and s[i][j] != g[i][j])

def h_manhattan(s, g):
    pos = {g[i][j]: (i, j) for i in range(3) for j in range(3)}
    return sum(abs(i - pos[s[i][j]][0]) + abs(j - pos[s[i][j]][1])
               for i in range(3) for j in range(3) if s[i][j] != 0)

def is_solvable(start, goal):
    def inv(s):
        f = [v for row in s for v in row if v != 0]
        return sum(1 for i in range(len(f)) for j in range(i+1, len(f)) if f[i] > f[j])
    return inv(start) % 2 == inv(goal) % 2

def trace_path(node):
    path, n = [], node
    while n: path.append({'state': n['state'], 'action': n['action']}); n = n['parent']
    return list(reversed(path))

def greedy_search(start, goal, hfn, cb):
    h0   = hfn(start, goal)
    root = {'state': start, 'parent': None, 'action': None, 'h': h0, 'g': 0, 'f': h0}
    heap = [(h0, 0, root)]
    seen = set(); cnt = 0; exp = 0
    while heap:
        if not cb('alive', {}): return
        _, _, cur = heapq.heappop(heap)
        ct = state_to_tuple(cur['state'])
        if ct in seen: continue
        seen.add(ct); exp += 1
        cb('explore', {'node': cur, 'exp': exp, 'frn': len(heap)})
        if cur['state'] == goal:
            cb('done', {'path': trace_path(cur), 'exp': exp, 'frn': len(heap)}); return
        for a in get_actions(cur['state']):
            ns = do_move(cur['state'], a)
            if state_to_tuple(ns) not in seen:
                cnt += 1; h = hfn(ns, goal)
                heapq.heappush(heap, (h, cnt,
                    {'state': ns, 'parent': cur, 'action': a, 'h': h, 'g': 0, 'f': h}))
    cb('fail', {'exp': exp})

def astar_search(start, goal, hfn, cb):
    h0   = hfn(start, goal)
    root = {'state': start, 'parent': None, 'action': None, 'h': h0, 'g': 0, 'f': h0}
    heap = [(h0, 0, root)]
    best = {state_to_tuple(start): 0}; cnt = 0; exp = 0
    while heap:
        if not cb('alive', {}): return
        _, _, cur = heapq.heappop(heap)
        exp += 1
        cb('explore', {'node': cur, 'exp': exp, 'frn': len(heap)})
        if cur['state'] == goal:
            cb('done', {'path': trace_path(cur), 'exp': exp, 'frn': len(heap)}); return
        for a in get_actions(cur['state']):
            ns  = do_move(cur['state'], a)
            nt  = state_to_tuple(ns)
            g2  = cur['g'] + 1
            if nt not in best or g2 < best[nt]:
                best[nt] = g2; cnt += 1
                h = hfn(ns, goal); f2 = g2 + h
                heapq.heappush(heap, (f2, cnt,
                    {'state': ns, 'parent': cur, 'action': a, 'h': h, 'g': g2, 'f': f2}))
    cb('fail', {'exp': exp})

# ══════════════════════════════════════════════════════
#  MÀU SẮC  –  Vivid Neon-Dark
# ══════════════════════════════════════════════════════
# Root / Header
ROOT_BG   = '#07090F'
HDR_BG    = '#080E20'
HDR_LINE  = '#1E3A8A'

# Combobox (đen)
CB_BG     = '#09111F'
CB_FG     = '#00CFFF'

# BLUE section (trạng thái đầu / đích)
BLU_BG    = '#040B1A'
BLU_BDR   = '#00C8FF'     # vivid cyan
BLU_TILE  = '#0B2550'
BLU_TXT   = '#00E5FF'
BLU_EMPTY = '#040B1A'
GOAL_TILE = '#083A22'
GOAL_TXT  = '#00FF88'
GOAL_EM   = '#030F07'

# GREEN section (bảng hiện tại + đường đi)
GRN_BG    = '#03100A'
GRN_BDR   = '#00FF88'     # vivid green
GRN_TILE  = '#083A22'
GRN_TXT   = '#00FF88'
GRN_EM    = '#03100A'
GRN_ACT   = '#0055BB'     # highlight moving tile

# RED section (log + thông tin)
RED_BG    = '#0D0305'
RED_BDR   = '#FF3366'     # vivid red-pink

# Text
TXT_W     = '#FFFFFF'
TXT_M     = '#A0C0DC'
TXT_D     = '#3A5468'

# Stats / costs
CLR_EXP   = '#00FF88'
CLR_FRN   = '#FFD700'
CLR_STP   = '#CC88FF'
CLR_H     = '#00CFFF'
CLR_G     = '#CC88FF'
CLR_F     = '#FF6090'
CLR_ALGO  = '#FFD700'
CLR_OK    = '#00FF88'
CLR_FAIL  = '#FF3366'
CLR_WARN  = '#FFD700'

# Buttons
BTN_SOLVE = '#005C33'
BTN_RAND  = '#8A4000'
BTN_RESET = '#7A0A20'
BTN_APPLY = '#003A7A'

# ══════════════════════════════════════════════════════
#  CONFIG
# ══════════════════════════════════════════════════════
ALGOS = {
    'Greedy — Misplaced Tiles':    ('greedy', 'misplaced'),
    'Greedy — Manhattan Distance': ('greedy', 'manhattan'),
    'A* — Misplaced Tiles':        ('astar',  'misplaced'),
    'A* — Manhattan Distance':     ('astar',  'manhattan'),
}

DEFAULT_START = [[2, 1, 4], [7, 0, 6], [5, 3, 8]]
DEFAULT_GOAL  = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]

# ══════════════════════════════════════════════════════
#  APPLICATION
# ══════════════════════════════════════════════════════
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Informed Search — 8-Puzzle Solver')
        self.configure(bg=ROOT_BG)
        self.resizable(True, True)
        self.minsize(980, 580)

        self._start   = copy.deepcopy(DEFAULT_START)
        self._goal    = copy.deepcopy(DEFAULT_GOAL)
        self._cur     = copy.deepcopy(DEFAULT_START)
        self._running = False
        self._algo_var = tk.StringVar(value=list(ALGOS.keys())[0])

        # fonts
        self.F_TTL  = ('Segoe UI', 13, 'bold')
        self.F_HDR  = ('Segoe UI', 11, 'bold')
        self.F_TILE = ('Segoe UI', 15, 'bold')
        self.F_BIG  = ('Segoe UI', 17, 'bold')
        self.F_MINI = ('Segoe UI', 9,  'bold')
        self.F_BTN  = ('Segoe UI', 10, 'bold')
        self.F_BODY = ('Segoe UI', 10, 'bold')
        self.F_MONO = ('Consolas', 9)
        self.F_BDGE = ('Segoe UI', 11, 'bold')
        self.F_STAT = ('Segoe UI', 10, 'bold')

        self._build()

    # ──────────────────────────────────────────
    #  BUILD UI
    # ──────────────────────────────────────────
    def _build(self):
        self._build_header()

        body = tk.Frame(self, bg=ROOT_BG)
        body.pack(fill=tk.BOTH, expand=True, padx=7, pady=(0, 7))
        body.columnconfigure(0, minsize=470, weight=0)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=2, minsize=220)
        body.rowconfigure(1, weight=3, minsize=280)

        # BLUE – top-left
        blue = self._section_frame(body, BLU_BG, BLU_BDR)
        blue.grid(row=0, column=0, sticky='nsew', padx=(0, 5), pady=(0, 5))
        self._build_blue(blue)

        # GREEN – bottom-left
        grn = self._section_frame(body, GRN_BG, GRN_BDR)
        grn.grid(row=1, column=0, sticky='nsew', padx=(0, 5))
        self._build_green(grn)

        # RED – right, spans both rows
        red = self._section_frame(body, RED_BG, RED_BDR)
        red.grid(row=0, column=1, rowspan=2, sticky='nsew')
        self._build_red(red)

    # ── HEADER ────────────────────────────────
    def _build_header(self):
        hdr = tk.Frame(self, bg=HDR_BG, height=48)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)

        # Title
        tk.Label(hdr, text='8-Puzzle  —  Informed Search',
                 bg=HDR_BG, fg=TXT_W, font=self.F_TTL
                 ).pack(side=tk.LEFT, padx=(14, 10))

        self._vsep(hdr)

        # Combobox (dark/black look per wireframe)
        tk.Label(hdr, text='Thuat toan:', bg=HDR_BG, fg=TXT_M,
                 font=self.F_BODY).pack(side=tk.LEFT, padx=(4, 3))
        self._style_combo()
        cb = ttk.Combobox(hdr, textvariable=self._algo_var,
                          values=list(ALGOS.keys()),
                          state='readonly', font=self.F_BODY, width=26)
        cb.pack(side=tk.LEFT, pady=10)
        cb.bind('<<ComboboxSelected>>', lambda e: self._on_algo_change())

        self._vsep(hdr)

        # Action buttons
        self._btn(hdr, 'Giai',   BTN_SOLVE, self._solve).pack(side=tk.LEFT, padx=3)
        self._btn(hdr, 'Reset',  BTN_RESET, self._reset).pack(side=tk.LEFT, padx=3)

        # Stats on the right
        sf = tk.Frame(hdr, bg=HDR_BG)
        sf.pack(side=tk.RIGHT, padx=10)
        self._lbl_stp = self._badge(sf, 'Steps',    '—',  CLR_STP)
        self._lbl_frn = self._badge(sf, 'Frontier', '0',  CLR_FRN)
        self._lbl_exp = self._badge(sf, 'Explored', '0',  CLR_EXP)

    # ── BLUE SECTION (Trạng thái đầu + đích) ─
    def _build_blue(self, parent):
        # Section title bar
        bar = tk.Frame(parent, bg=BLU_BDR, height=2)
        bar.pack(fill=tk.X)
        inner = tk.Frame(parent, bg=BLU_BG)
        inner.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)
        inner.columnconfigure(0, weight=1)
        inner.columnconfigure(1, weight=1)

        # ── Column headers
        tk.Label(inner, text='Trang Thai Dau', bg=BLU_BG, fg=BLU_BDR,
                 font=self.F_HDR).grid(row=0, column=0, pady=(0, 4))
        tk.Label(inner, text='Trang Thai Dich', bg=BLU_BG, fg=GRN_BDR,
                 font=self.F_HDR).grid(row=0, column=1, pady=(0, 4))

        # ── Start grid (editable entries)
        self._sv = [[tk.StringVar() for _ in range(3)] for _ in range(3)]
        self._se = [[None]*3 for _ in range(3)]
        sgf = tk.Frame(inner, bg=BLU_BG)
        sgf.grid(row=1, column=0, padx=6, pady=2)
        for i in range(3):
            for j in range(3):
                v = self._start[i][j]
                self._sv[i][j].set('' if v == 0 else str(v))
                e = tk.Entry(sgf, textvariable=self._sv[i][j], width=3,
                             justify='center', font=self.F_TILE,
                             bg=BLU_EMPTY if v == 0 else BLU_TILE,
                             fg=BLU_TXT, insertbackground=TXT_W,
                             relief='flat', bd=0,
                             highlightthickness=2,
                             highlightbackground='#0B1A30',
                             highlightcolor=BLU_BDR)
                e.grid(row=i, column=j, padx=2, pady=2, ipadx=7, ipady=5)
                self._se[i][j] = e

        # ── Goal grid (display labels)
        self._ge = [[None]*3 for _ in range(3)]
        ggf = tk.Frame(inner, bg=BLU_BG)
        ggf.grid(row=1, column=1, padx=6, pady=2)
        for i in range(3):
            for j in range(3):
                v = self._goal[i][j]
                lbl = tk.Label(ggf,
                               text=str(v) if v != 0 else '',
                               width=2,
                               bg=GOAL_EM if v == 0 else GOAL_TILE,
                               fg=GOAL_TXT, font=self.F_TILE,
                               relief='flat',
                               highlightbackground='#051208',
                               highlightthickness=2)
                lbl.grid(row=i, column=j, padx=2, pady=2, ipadx=9, ipady=5)
                self._ge[i][j] = lbl

        # ── Buttons row
        bf = tk.Frame(inner, bg=BLU_BG)
        bf.grid(row=2, column=0, columnspan=2, pady=(6, 0), sticky='w', padx=6)
        self._btn(bf, 'Ngau Nhien', BTN_RAND, self._randomize).pack(side=tk.LEFT, padx=2)
        self._btn(bf, 'Ap Dung',    BTN_APPLY, self._apply_start).pack(side=tk.LEFT, padx=2)

    # ── GREEN SECTION (Bảng hiện tại + Đường đi) ─
    def _build_green(self, parent):
        bar = tk.Frame(parent, bg=GRN_BDR, height=2)
        bar.pack(fill=tk.X)
        inner = tk.Frame(parent, bg=GRN_BG)
        inner.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

        # Left: current animated board
        left = tk.Frame(inner, bg=GRN_BG)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 4))

        tk.Label(left, text='Bang Hien Tai', bg=GRN_BG, fg=GRN_BDR,
                 font=self.F_HDR).pack(anchor='w', pady=(0, 4))
        bf = tk.Frame(left, bg=GRN_BG)
        bf.pack()
        self._ct = [[None]*3 for _ in range(3)]
        for i in range(3):
            for j in range(3):
                v = self._cur[i][j]
                lbl = tk.Label(bf, text=str(v) if v != 0 else '',
                               width=2,
                               bg=GRN_EM if v == 0 else GRN_TILE,
                               fg=GRN_TXT, font=self.F_BIG,
                               relief='flat',
                               highlightbackground='#051208',
                               highlightthickness=2)
                lbl.grid(row=i, column=j, padx=3, pady=3, ipadx=10, ipady=8)
                self._ct[i][j] = lbl

        # Divider
        tk.Frame(inner, bg=GRN_BDR, width=2).pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=4)

        # Right: path scroll area
        right = tk.Frame(inner, bg=GRN_BG)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(right, text='Duong Di: Start  ->  Goal', bg=GRN_BG, fg=GRN_BDR,
                 font=self.F_HDR).pack(anchor='w', pady=(0, 4))

        cf = tk.Frame(right, bg=GRN_BG)
        cf.pack(fill=tk.BOTH, expand=True)

        self._pc = tk.Canvas(cf, bg=GRN_BG, highlightthickness=0)
        hsb = tk.Scrollbar(cf, orient=tk.HORIZONTAL, command=self._pc.xview)
        self._pc.configure(xscrollcommand=hsb.set)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self._pc.pack(fill=tk.BOTH, expand=True)

        self._pi = tk.Frame(self._pc, bg=GRN_BG)
        self._pw = self._pc.create_window((0, 0), window=self._pi, anchor='nw')
        self._pi.bind('<Configure>', lambda e: self._pc.configure(
            scrollregion=self._pc.bbox('all')))

        tk.Label(self._pi, text='Chua co duong di...',
                 bg=GRN_BG, fg=TXT_D, font=self.F_BODY).pack(padx=20, pady=16)

    # ── RED SECTION (Thông tin + Nhật ký) ────
    def _build_red(self, parent):
        bar = tk.Frame(parent, bg=RED_BDR, height=2)
        bar.pack(fill=tk.X)
        inner = tk.Frame(parent, bg=RED_BG)
        inner.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

        # ── Cost info
        tk.Label(inner, text='Thong Tin Thuat Toan', bg=RED_BG, fg=RED_BDR,
                 font=self.F_HDR).pack(anchor='w')

        self._cv = {}
        info_rows = [
            ('h(n)', 'Heuristic (ô sai / Manhattan)', CLR_H),
            ('g(n)', 'Chi phí thực tế (A*)',           CLR_G),
            ('f(n)', 'f = g + h  (A*)',                CLR_F),
            ('algo', 'Thuật toán',                     CLR_ALGO),
        ]
        for key, desc, clr in info_rows:
            rf = tk.Frame(inner, bg=RED_BG)
            rf.pack(fill=tk.X, pady=2)
            tk.Label(rf, text=f'{key}:', bg=RED_BG, fg=TXT_M,
                     font=self.F_STAT, width=6, anchor='w').pack(side=tk.LEFT)
            tk.Label(rf, text=desc, bg=RED_BG, fg=TXT_D,
                     font=self.F_STAT).pack(side=tk.LEFT)
            v = tk.Label(rf, text='—', bg=RED_BG, fg=clr, font=self.F_BDGE)
            v.pack(side=tk.RIGHT)
            self._cv[key] = v

        self._status_lbl = tk.Label(inner, text='San sang', bg=RED_BG,
                                    fg=CLR_OK, font=self.F_HDR)
        self._status_lbl.pack(anchor='w', pady=(6, 0))

        # Separator
        tk.Frame(inner, bg=RED_BDR, height=1).pack(fill=tk.X, pady=(10, 6))

        # ── Log
        tk.Label(inner, text='Nhat Ky Kham Pha', bg=RED_BG, fg=RED_BDR,
                 font=self.F_HDR).pack(anchor='w', pady=(0, 4))

        lf = tk.Frame(inner, bg=RED_BG)
        lf.pack(fill=tk.BOTH, expand=True)

        self._log = tk.Text(lf, bg='#080204', fg=TXT_M, font=self.F_MONO,
                            relief='flat', wrap=tk.NONE, state=tk.DISABLED,
                            insertbackground=TXT_W)
        vsb = tk.Scrollbar(lf, orient=tk.VERTICAL, command=self._log.yview)
        hsb2 = tk.Scrollbar(lf, orient=tk.HORIZONTAL, command=self._log.xview)
        self._log.configure(yscrollcommand=vsb.set, xscrollcommand=hsb2.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb2.pack(side=tk.BOTTOM, fill=tk.X)
        self._log.pack(fill=tk.BOTH, expand=True)

        self._log.tag_config('explore',  foreground=CLR_EXP)
        self._log.tag_config('frontier', foreground=CLR_FRN)
        self._log.tag_config('done',     foreground=CLR_OK)
        self._log.tag_config('fail',     foreground=CLR_FAIL)
        self._log.tag_config('info',     foreground=CLR_STP)

    # ──────────────────────────────────────────
    #  WIDGET HELPERS
    # ──────────────────────────────────────────
    def _section_frame(self, parent, bg, bdr):
        return tk.Frame(parent, bg=bg, highlightbackground=bdr, highlightthickness=2)

    def _vsep(self, parent):
        tk.Frame(parent, bg=HDR_LINE, width=1, height=28).pack(
            side=tk.LEFT, padx=8, pady=10)

    def _btn(self, parent, text, color, cmd):
        b = tk.Button(parent, text=text, command=cmd, bg=color, fg=TXT_W,
                      font=self.F_BTN, relief='flat', cursor='hand2',
                      activebackground=color, activeforeground=TXT_W,
                      padx=10, pady=5, bd=0)
        light = self._lighter(color)
        b.bind('<Enter>', lambda e: b.config(bg=light))
        b.bind('<Leave>', lambda e: b.config(bg=color))
        return b

    def _badge(self, parent, label, val, clr):
        f = tk.Frame(parent, bg=HDR_BG)
        f.pack(side=tk.RIGHT, padx=8)
        tk.Label(f, text=label, bg=HDR_BG, fg=TXT_M, font=self.F_STAT).pack()
        lv = tk.Label(f, text=val, bg=HDR_BG, fg=clr, font=self.F_BDGE)
        lv.pack()
        return lv

    @staticmethod
    def _lighter(h):
        r, g, b = int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)
        return f'#{min(255,r+40):02x}{min(255,g+40):02x}{min(255,b+40):02x}'

    def _style_combo(self):
        s = ttk.Style(); s.theme_use('default')
        s.configure('TCombobox',
                    fieldbackground=CB_BG, background=CB_BG,
                    foreground=CB_FG, selectbackground=CB_BG,
                    selectforeground=CB_FG, borderwidth=0, arrowcolor=CB_FG)
        s.map('TCombobox',
              fieldbackground=[('readonly', CB_BG)],
              foreground=[('readonly', CB_FG)],
              background=[('readonly', CB_BG)])

    # ──────────────────────────────────────────
    #  LOG
    # ──────────────────────────────────────────
    def _log_write(self, msg, tag=''):
        self._log.config(state=tk.NORMAL)
        self._log.insert(tk.END, msg + '\n', tag)
        self._log.see(tk.END)
        self._log.config(state=tk.DISABLED)

    def _log_clear(self):
        self._log.config(state=tk.NORMAL)
        self._log.delete('1.0', tk.END)
        self._log.config(state=tk.DISABLED)

    # ──────────────────────────────────────────
    #  BOARD UPDATES
    # ──────────────────────────────────────────
    def _refresh_start_entries(self):
        for i in range(3):
            for j in range(3):
                v = self._start[i][j]
                self._sv[i][j].set('' if v == 0 else str(v))
                self._se[i][j].config(bg=BLU_EMPTY if v == 0 else BLU_TILE)

    def _update_cur_board(self, state, highlight=None):
        for i in range(3):
            for j in range(3):
                v   = state[i][j]
                em  = (v == 0)
                act = (highlight == (i, j))
                bg  = GRN_EM if em else (GRN_ACT if act else GRN_TILE)
                self._ct[i][j].config(text=str(v) if not em else '', bg=bg, fg=GRN_TXT)

    def _update_costs(self, node):
        algo_type = ALGOS[self._algo_var.get()][0]
        is_astar  = (algo_type == 'astar')
        if node is None:
            self._cv['h(n)'].config(text='—')
            self._cv['g(n)'].config(text='—' if is_astar else 'N/A')
            self._cv['f(n)'].config(text='—' if is_astar else 'N/A')
            self._cv['algo'].config(text='A*' if is_astar else 'Greedy')
        else:
            self._cv['h(n)'].config(text=str(node.get('h', '—')))
            self._cv['g(n)'].config(text=str(node.get('g', '—')) if is_astar else 'N/A')
            self._cv['f(n)'].config(text=str(node.get('f', '—')) if is_astar else 'N/A')
            self._cv['algo'].config(text='A*' if is_astar else 'Greedy')

    def _update_stats(self, exp, frn, stp='—'):
        self._lbl_exp.config(text=str(exp))
        self._lbl_frn.config(text=str(frn))
        self._lbl_stp.config(text=str(stp))

    def _clear_path(self):
        for w in self._pi.winfo_children(): w.destroy()

    def _show_path(self, path):
        self._clear_path()
        n = len(path)
        for idx, step in enumerate(path):
            st  = step['state']
            act = step.get('action') or 'Start'
            sf  = tk.Frame(self._pi, bg=GRN_BG)
            sf.pack(side=tk.LEFT, padx=3, pady=4)
            # label
            if idx == 0:        lt, lc = 'Start', BLU_BDR
            elif idx == n - 1:  lt, lc = 'Goal', GRN_BDR
            else:               lt, lc = f'{act}', GRN_TXT
            tk.Label(sf, text=lt, bg=GRN_BG, fg=lc, font=self.F_MINI).pack()
            # mini grid
            gf = tk.Frame(sf, bg=GRN_BG)
            gf.pack()
            for i in range(3):
                for j in range(3):
                    v = st[i][j]
                    em = (v == 0)
                    bg = GRN_EM if em else GRN_TILE
                    fg = GRN_TXT if not em else GRN_BG
                    tk.Label(gf, text=str(v) if not em else '', width=2,
                             bg=bg, fg=fg, font=self.F_MINI, relief='flat',
                             highlightbackground='#051208',
                             highlightthickness=1
                             ).grid(row=i, column=j, padx=1, pady=1, ipadx=3, ipady=2)
        self._pc.update_idletasks()
        self._pc.configure(scrollregion=self._pc.bbox('all'))

    # ──────────────────────────────────────────
    #  USER ACTIONS
    # ──────────────────────────────────────────
    def _on_algo_change(self):
        self._update_costs(None)

    def _randomize(self):
        nums = list(range(9)); random.shuffle(nums)
        self._start = [nums[:3], nums[3:6], nums[6:]]
        self._cur   = copy.deepcopy(self._start)
        self._refresh_start_entries()
        self._update_cur_board(self._cur)

    def _apply_start(self):
        s, used = [], set()
        for i in range(3):
            row = []
            for j in range(3):
                raw = self._sv[i][j].get().strip()
                if raw == '': val = 0
                elif raw.isdigit(): val = int(raw)
                else:
                    messagebox.showerror('Lỗi', f'Giá trị "{raw}" không hợp lệ!'); return
                if val > 8:
                    messagebox.showerror('Lỗi', f'Số {val} > 8!'); return
                if val in used:
                    messagebox.showerror('Lỗi', f'Số {val} bị trùng!'); return
                used.add(val); row.append(val)
            s.append(row)
        if used != set(range(9)):
            messagebox.showerror('Lỗi', 'Cần đủ các số 0–8!'); return
        self._start = s
        self._cur   = copy.deepcopy(s)
        self._update_cur_board(self._cur)
        self._status_lbl.config(text='Da cap nhat trang thai dau', fg=BLU_BDR)

    def _reset(self):
        self._running = False
        self._start   = copy.deepcopy(DEFAULT_START)
        self._goal    = copy.deepcopy(DEFAULT_GOAL)
        self._cur     = copy.deepcopy(DEFAULT_START)
        self._refresh_start_entries()
        self._update_cur_board(self._cur)
        self._log_clear()
        self._clear_path()
        tk.Label(self._pi, text='Chua co duong di...',
                 bg=GRN_BG, fg=TXT_D, font=self.F_BODY).pack(padx=20, pady=16)
        self._update_stats(0, 0)
        self._update_costs(None)
        self._status_lbl.config(text='San sang', fg=CLR_OK)

    # ──────────────────────────────────────────
    #  SOLVE
    # ──────────────────────────────────────────
    def _solve(self):
        if self._running: return
        if not is_solvable(self._start, self._goal):
            messagebox.showwarning('Không giải được',
                                   'Trạng thái này không thể giải!\n'
                                   'Hãy thử lại hoặc bấm Ngẫu Nhiên.')
            return
        self._running = True
        self._log_clear()
        self._clear_path()
        self._update_stats(0, 0)
        self._update_costs(None)
        self._status_lbl.config(text='Dang giai...', fg=CLR_WARN)

        key = self._algo_var.get()
        algo_type, heur_type = ALGOS[key]
        hfn = h_manhattan if heur_type == 'manhattan' else h_misplaced
        fn  = astar_search if algo_type == 'astar' else greedy_search

        self._log_write(f'[BẮT ĐẦU]  {key}', 'info')
        start = copy.deepcopy(self._start)
        goal  = copy.deepcopy(self._goal)

        threading.Thread(target=fn,
                         args=(start, goal, hfn, self._cb),
                         daemon=True).start()

    def _cb(self, event, data):
        if event == 'alive':
            return self._running
        if event == 'explore':
            node = data['node']
            exp  = data['exp']
            frn  = data['frn']
            self.after(0, lambda n=node, e=exp, f=frn: self._on_explore(n, e, f))
            time.sleep(0.05)
        elif event == 'done':
            path, exp, frn = data['path'], data['exp'], data['frn']
            self.after(0, lambda p=path, e=exp, f=frn: self._on_done(p, e, f))
        elif event == 'fail':
            exp = data['exp']
            self.after(0, lambda e=exp: self._on_fail(e))

    def _on_explore(self, node, exp, frn):
        st = node['state']
        self._update_cur_board(st)
        self._update_stats(exp, frn)
        self._update_costs(node)
        algo_type = ALGOS[self._algo_var.get()][0]
        row = [v for r in st for v in r]
        msg = f'[#{exp:>4}] {row}   h={node["h"]}'
        if algo_type == 'astar':
            msg += f'  g={node["g"]}  f={node["f"]}'
        self._log_write(msg, 'explore')

    def _on_done(self, path, exp, frn):
        self._running = False
        steps = len(path) - 1
        self._update_stats(exp, frn, steps)
        self._status_lbl.config(text=f'Tim thay!  {steps} buoc', fg=CLR_OK)
        self._log_write(f'\n[XONG]  {steps} buoc — da kham pha {exp} node\n', 'done')
        self._show_path(path)
        self._animate(path)

    def _on_fail(self, exp):
        self._running = False
        self._status_lbl.config(text='Khong tim thay duong di!', fg=CLR_FAIL)
        self._log_write(f'\n[THAT BAI]  Da kham pha {exp} node, khong co duong di.\n', 'fail')

    def _animate(self, path):
        self._running = True  # allow animation loop
        def step(idx):
            if not self._running or idx >= len(path): return
            st = path[idx]['state']
            hi = None
            if idx > 0:
                pv = path[idx - 1]['state']
                for i in range(3):
                    for j in range(3):
                        if pv[i][j] != st[i][j] and st[i][j] != 0:
                            hi = (i, j)
            self._update_cur_board(st, hi)
            delay = 400
            self.after(delay, lambda: step(idx + 1))
        step(0)


# ══════════════════════════════════════════════════════
if __name__ == '__main__':
    App().mainloop()
