"""
Belief-State BFS (8-Puzzle)
"""

import copy, random, threading, time
import tkinter as tk
from collections import deque

# ═══════════════════════════════════════════════════════════
#  ALGORITHM
# ═══════════════════════════════════════════════════════════

GOAL_STATE = ((1, 2, 3), (8, 0, 4), (7, 6, 5))

state_A = ((1, 0, 3),
           (8, 2, 4),
           (7, 6, 5))

state_B = ((0, 2, 3),
           (1, 8, 4),
           (7, 6, 5))
start_belief = frozenset([state_A, state_B])

def random_puzzle_state():
    nums = list(range(9))
    random.shuffle(nums)
    return tuple(tuple(nums[i * 3 + j] for j in range(3)) for i in range(3))


def generate_random_belief(n=2):
    states = []
    while len(states) < n:
        s = random_puzzle_state()
        if s != GOAL_STATE and s not in states:
            states.append(s)
    return frozenset(states)


def move_blank(state, action):
    x = y = -1
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                x, y = i, j
    nx, ny = x, y
    if action == 'U':   nx -= 1
    elif action == 'D': nx += 1
    elif action == 'L': ny -= 1
    elif action == 'R': ny += 1
    if 0 <= nx < 3 and 0 <= ny < 3:
        lst = [list(r) for r in state]
        lst[x][y], lst[nx][ny] = lst[nx][ny], lst[x][y]
        return tuple(tuple(r) for r in lst)
    return state


def belief_state_bfs(start_belief, goal, cb):
    frontier      = deque([(start_belief, [])])
    explored      = {start_belief}
    actions       = ['U', 'D', 'L', 'R']
    nodes_exp     = [0]

    while frontier:
        if not cb('alive', {}):
            return
        cur_belief, path = frontier.popleft()
        nodes_exp[0] += 1
        cb('belief_step', {
            'belief': cur_belief, 'path': path,
            'action': path[-1] if path else None,
            'step': len(path), 'exp': nodes_exp[0], 'frn': len(frontier),
        })
        time.sleep(0.18)

        if all(s == goal for s in cur_belief):
            cb('done', {'path': path, 'belief': cur_belief,
                        'exp': nodes_exp[0], 'steps': len(path)})
            return

        for act in actions:
            nxt = frozenset(move_blank(s, act) for s in cur_belief)
            if nxt not in explored:
                explored.add(nxt)
                frontier.append((nxt, path + [act]))

    cb('fail', {'exp': nodes_exp[0]})


# ═══════════════════════════════════════════════════════════
#  COLORS
# ═══════════════════════════════════════════════════════════
ROOT_BG  = '#F5F7FA'
HDR_BG   = '#1A2E4A';  HDR_LINE = '#3D6A9A'

GOAL_BG  = '#E8F5E9';  GOAL_BDR = '#2E7D32'
GOAL_T   = '#A5D6A7';  GOAL_TXT = '#1B5E20';  GOAL_EM  = '#E8F5E9'

INIT_BG  = '#E3F2FD';  INIT_BDR = '#1565C0'
INIT_T   = '#90CAF9';  INIT_TXT = '#0D3B66';  INIT_EM  = '#E3F2FD'

MNT_BG   = '#E0F7FA';  MNT_BDR  = '#00838F'
MNT_T    = '#80DEEA';  MNT_TXT  = '#006064';  MNT_EM   = '#E0F7FA'

BLF_BG   = '#EEF6FF';  BLF_BDR  = '#00695C';  BLF_LOG  = '#F5FEFF'

TXT_W    = '#FFFFFF';  TXT_DARK = '#1A2440'
TXT_MID  = '#4A6080';  TXT_DIM  = '#90A4B8'

CLR_OK   = '#2E7D32';  CLR_FAIL = '#C62828';  CLR_WARN = '#E65100'
CLR_ALGO = '#1565C0';  CLR_STEPS= '#7B1FA2'
CLR_EXP  = '#00897B';  CLR_FRN  = '#F57F17';  CLR_BSIZ = '#AD1457'

BTN_SOLVE = '#1565C0'; BTN_RESET = '#B71C1C'

# Fonts
F_TTL  = ('Segoe UI', 13, 'bold')
F_HDR  = ('Segoe UI', 11, 'bold')
F_BODY = ('Segoe UI', 10, 'bold')
F_STAT = ('Segoe UI', 10, 'bold')
F_MINI = ('Segoe UI',  9, 'bold')
F_BTN  = ('Segoe UI', 10, 'bold')
F_BDGE = ('Segoe UI', 11, 'bold')
F_MONO = ('Consolas',  9)
# Tile fonts — dung cho grid 3x3
F_TILE_LG = ('Segoe UI', 13, 'bold')   # goal state (lon)
F_TILE_SM = ('Segoe UI', 11, 'bold')   # cac grid nho


# ═══════════════════════════════════════════════════════════
#  Helper: ve 1 grid 3x3
# ═══════════════════════════════════════════════════════════
def make_grid(parent, state, bg_tile, bg_empty, fg_tile,
              font=F_TILE_SM, pad_x=2, pad_y=2, ipx=6, ipy=3):
    """Tra ve list[list[Label]] de co the cap nhat sau."""
    labels = [[None]*3 for _ in range(3)]
    for i in range(3):
        for j in range(3):
            v = state[i][j]
            lbl = tk.Label(parent,
                           text=str(v) if v != 0 else '',
                           width=2,
                           bg=bg_empty if v == 0 else bg_tile,
                           fg=fg_tile, font=font, relief='flat',
                           highlightbackground='#B2DFDB',
                           highlightthickness=1)
            lbl.grid(row=i, column=j,
                     padx=pad_x, pady=pad_y,
                     ipadx=ipx, ipady=ipy)
            labels[i][j] = lbl
    return labels


def update_grid(labels, state, bg_tile, bg_empty, fg_tile, goal=None):
    """Cap nhat noi dung grid (khong tao lai)."""
    for i in range(3):
        for j in range(3):
            v = state[i][j]
            in_place = (goal and v != 0 and v == goal[i][j])
            bg = bg_empty if v == 0 else ('#69F0AE' if in_place else bg_tile)
            labels[i][j].config(text=str(v) if v != 0 else '', bg=bg)


# ═══════════════════════════════════════════════════════════
#  BeliefPanel (right)
# ═══════════════════════════════════════════════════════════
class BeliefPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BLF_BG,
                         highlightbackground=BLF_BDR, highlightthickness=2)
        self._build()

    def _build(self):
        tk.Frame(self, bg=BLF_BDR, height=4).pack(fill=tk.X)
        inn = tk.Frame(self, bg=BLF_BG)
        inn.pack(fill=tk.BOTH, expand=True, padx=14, pady=10)

        tk.Label(inn, text='Belief-State Search — Thong Tin',
                 bg=BLF_BG, fg=BLF_BDR, font=F_HDR).pack(anchor='w', pady=(0, 6))

        self._cv = {}
        rows = [
            ('Thuat toan',  'Belief-State BFS',          CLR_ALGO),
            ('Belief Size', 'so ma tran hien tai',       CLR_BSIZ),
            ('Buoc',        'so hanh dong da thuc hien', CLR_STEPS),
            ('Hanh dong',   'lenh robot vua bam',        '#E65100'),
            ('Nodes KP',    'nodes da kham pha',         CLR_EXP),
            ('Frontier',    'hang doi hien tai',         CLR_FRN),
        ]
        for key, desc, clr in rows:
            rf = tk.Frame(inn, bg=BLF_BG); rf.pack(fill=tk.X, pady=2)
            tk.Label(rf, text=f'{key}:', bg=BLF_BG, fg=TXT_MID,
                     font=F_STAT, width=13, anchor='w').pack(side=tk.LEFT)
            tk.Label(rf, text=desc, bg=BLF_BG, fg=TXT_DIM,
                     font=F_STAT).pack(side=tk.LEFT)
            v = tk.Label(rf, text='—', bg=BLF_BG, fg=clr, font=F_BDGE)
            v.pack(side=tk.RIGHT)
            self._cv[key] = v
        self._cv['Thuat toan'].config(text='BFS')

        self._status = tk.Label(inn, text='San sang', bg=BLF_BG,
                                fg=CLR_OK, font=F_HDR)
        self._status.pack(anchor='w', pady=(8, 0))

        tk.Frame(inn, bg=BLF_BDR, height=1).pack(fill=tk.X, pady=(10, 4))
        tk.Label(inn, text='Nhat Ky Kham Pha', bg=BLF_BG, fg=BLF_BDR,
                 font=F_HDR).pack(anchor='w', pady=(0, 4))

        lf = tk.Frame(inn, bg=BLF_BG); lf.pack(fill=tk.BOTH, expand=True)
        self._log = tk.Text(lf, bg=BLF_LOG, fg=TXT_DARK, font=F_MONO,
                            relief='flat', wrap=tk.NONE, state=tk.DISABLED,
                            highlightthickness=1, highlightbackground=BLF_BDR)
        vsb = tk.Scrollbar(lf, orient=tk.VERTICAL,   command=self._log.yview)
        hsb = tk.Scrollbar(lf, orient=tk.HORIZONTAL, command=self._log.xview)
        self._log.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side=tk.RIGHT,  fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self._log.pack(fill=tk.BOTH, expand=True)
        self._log.tag_config('start', foreground='#1565C0')
        self._log.tag_config('step',  foreground='#006064')
        self._log.tag_config('done',  foreground='#2E7D32')
        self._log.tag_config('fail',  foreground='#C62828')
        self._log.tag_config('info',  foreground='#AD1457')

    def set_status(self, text, clr=None):
        self._status.config(text=text, fg=clr or CLR_OK)

    def log_write(self, msg, tag=''):
        self._log.config(state=tk.NORMAL)
        self._log.insert(tk.END, msg + '\n', tag)
        self._log.see(tk.END)
        self._log.config(state=tk.DISABLED)

    def log_clear(self):
        self._log.config(state=tk.NORMAL)
        self._log.delete('1.0', tk.END)
        self._log.config(state=tk.DISABLED)

    def update_info(self, belief_size, step, action, exp, frn):
        self._cv['Belief Size'].config(text=str(belief_size))
        self._cv['Buoc'].config(text=str(step))
        self._cv['Hanh dong'].config(text=action if action else 'Khoi dau')
        self._cv['Nodes KP'].config(text=str(exp))
        self._cv['Frontier'].config(text=str(frn))

    def reset(self):
        for k, v in self._cv.items():
            v.config(text='—' if k != 'Thuat toan' else 'BFS')
        self._status.config(text='San sang', fg=CLR_OK)
        self.log_clear()


# ═══════════════════════════════════════════════════════════
#  APP
# ═══════════════════════════════════════════════════════════
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('8-Puzzle — Belief-State Space Search')
        self.configure(bg=ROOT_BG)
        self.resizable(True, True)
        self.minsize(1100, 640)

        # Initial belief (2 random states)
        self._start_belief = start_belief
        self._running = False
        self._build()

    # ─────────────────────────────────────────
    #  BUILD
    # ─────────────────────────────────────────
    def _build(self):
        self._build_header()

        body = tk.Frame(self, bg=ROOT_BG)
        body.pack(fill=tk.BOTH, expand=True, padx=7, pady=(0, 7))
        body.columnconfigure(0, minsize=490, weight=0)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=3, minsize=240)
        body.rowconfigure(1, weight=4, minsize=320)

        # Top-left: Goal + Initial Belief (2 cot)
        top_frame = tk.Frame(body, bg=ROOT_BG)
        top_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 6), pady=(0, 6))
        top_frame.columnconfigure(0, weight=1)
        top_frame.columnconfigure(1, weight=1)
        top_frame.rowconfigure(0, weight=1)
        self._build_goal_col(top_frame)
        self._build_init_col(top_frame)

        # Bottom-left: Belief set hien tai + Duong di
        bot = tk.Frame(body, bg=MNT_BG,
                       highlightbackground=MNT_BDR, highlightthickness=2)
        bot.grid(row=1, column=0, sticky='nsew', padx=(0, 6))
        self._build_bottom(bot)

        # Right panel
        self._blf_panel = BeliefPanel(body)
        self._blf_panel.grid(row=0, column=1, rowspan=2, sticky='nsew')

    # ── Header ──────────────────────────────
    def _build_header(self):
        hdr = tk.Frame(self, bg=HDR_BG, height=52)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Label(hdr, text='8-Puzzle Solver', bg=HDR_BG, fg=TXT_W,
                 font=F_TTL).pack(side=tk.LEFT, padx=(14, 4))
        tk.Label(hdr, text='Belief-State BFS', bg=HDR_BG, fg='#60C8FF',
                 font=F_TTL).pack(side=tk.LEFT, padx=(0, 10))
        tk.Frame(hdr, bg=HDR_LINE, width=1, height=30).pack(
            side=tk.LEFT, padx=8, pady=10)
        self._btn_solve = self._btn(hdr, 'Giai', BTN_SOLVE, self._solve)
        self._btn_solve.pack(side=tk.LEFT, padx=4)
        self._btn(hdr, 'Reset', BTN_RESET, self._reset).pack(side=tk.LEFT, padx=3)
        sf = tk.Frame(hdr, bg=HDR_BG); sf.pack(side=tk.RIGHT, padx=10)
        self._lbl_stp  = self._badge(sf, 'Steps',       '—', CLR_STEPS)
        self._lbl_bsiz = self._badge(sf, 'Belief Size', '?', CLR_BSIZ)
        self._lbl_exp  = self._badge(sf, 'Nodes KP',    '0', CLR_EXP)

    # ── Goal State column (left) ────────────
    def _build_goal_col(self, parent):
        f = tk.Frame(parent, bg=GOAL_BG,
                     highlightbackground=GOAL_BDR, highlightthickness=2)
        f.grid(row=0, column=0, sticky='nsew', padx=(0, 3), pady=0)
        tk.Frame(f, bg=GOAL_BDR, height=3).pack(fill=tk.X)
        inn = tk.Frame(f, bg=GOAL_BG)
        inn.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)
        tk.Label(inn, text='Trang Thai Dich', bg=GOAL_BG, fg=GOAL_BDR,
                 font=F_HDR).pack()
        tk.Label(inn, text='(Goal State)', bg=GOAL_BG, fg=TXT_MID,
                 font=('Segoe UI', 9)).pack(pady=(0, 6))
        gf = tk.Frame(inn, bg=GOAL_BG); gf.pack()
        make_grid(gf, GOAL_STATE, GOAL_T, GOAL_EM, GOAL_TXT,
                  font=F_TILE_LG, ipx=9, ipy=5)

    # ── Initial Belief column (right) ───────
    def _build_init_col(self, parent):
        self._init_col_frame = tk.Frame(parent, bg=INIT_BG,
                                        highlightbackground=INIT_BDR, highlightthickness=2)
        self._init_col_frame.grid(row=0, column=1, sticky='nsew', padx=(3, 0), pady=0)
        self._render_init_col()

    def _render_init_col(self):
        """Ve/cap nhat cot Initial Belief (duoc goi khi reset)."""
        for w in self._init_col_frame.winfo_children():
            w.destroy()
        tk.Frame(self._init_col_frame, bg=INIT_BDR, height=3).pack(fill=tk.X)
        inn = tk.Frame(self._init_col_frame, bg=INIT_BG)
        inn.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)
        tk.Label(inn, text='Tap Niem Tin Ban Dau', bg=INIT_BG, fg=INIT_BDR,
                 font=F_HDR).pack()
        n = len(self._start_belief)
        tk.Label(inn, text=f'({n} trang thai ngau nhien)', bg=INIT_BG, fg=TXT_MID,
                 font=('Segoe UI', 9)).pack(pady=(0, 4))
        states_f = tk.Frame(inn, bg=INIT_BG); states_f.pack()
        for col_i, state in enumerate(sorted(self._start_belief)):
            sf = tk.Frame(states_f, bg=INIT_BG)
            sf.grid(row=0, column=col_i, padx=5, pady=2)
            tk.Label(sf, text=f'Trang thai {col_i + 1}', bg=INIT_BG, fg=INIT_BDR,
                     font=F_MINI).pack(pady=(0, 2))
            gf = tk.Frame(sf, bg=INIT_BG); gf.pack()
            make_grid(gf, state, INIT_T, INIT_EM, INIT_TXT,
                      font=F_TILE_SM, ipx=6, ipy=3)

    # ── Bottom: Belief set + Path ────────────
    def _build_bottom(self, parent):
        tk.Frame(parent, bg=MNT_BDR, height=3).pack(fill=tk.X)
        inn = tk.Frame(parent, bg=MNT_BG)
        inn.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

        # --- Phan 1: Tap niem tin hien tai (weight=3) ---
        belief_frame = tk.Frame(inn, bg=MNT_BG)
        belief_frame.pack(fill=tk.BOTH, expand=True)

        bh = tk.Frame(belief_frame, bg=MNT_BG); bh.pack(fill=tk.X, pady=(0, 2))
        tk.Label(bh, text='Tap Niem Tin Hien Tai', bg=MNT_BG, fg=MNT_BDR,
                 font=F_HDR).pack(side=tk.LEFT)
        self._belief_count_lbl = tk.Label(bh, text='', bg=MNT_BG,
                                          fg=CLR_BSIZ, font=F_BODY)
        self._belief_count_lbl.pack(side=tk.LEFT, padx=6)

        seq_f = tk.Frame(belief_frame, bg=MNT_BG); seq_f.pack(fill=tk.X, pady=(0, 3))
        tk.Label(seq_f, text='Chuoi hanh dong:', bg=MNT_BG, fg=TXT_MID,
                 font=F_STAT).pack(side=tk.LEFT)
        self._action_seq_lbl = tk.Label(seq_f, text='(chua chay)',
                                        bg=MNT_BG, fg='#E65100', font=F_MONO)
        self._action_seq_lbl.pack(side=tk.LEFT, padx=4)

        bcf = tk.Frame(belief_frame, bg=MNT_BG); bcf.pack(fill=tk.BOTH, expand=True)
        self._belief_canvas = tk.Canvas(bcf, bg=MNT_BG, highlightthickness=0)
        bhsb = tk.Scrollbar(bcf, orient=tk.HORIZONTAL, command=self._belief_canvas.xview)
        self._belief_canvas.configure(xscrollcommand=bhsb.set)
        bhsb.pack(side=tk.BOTTOM, fill=tk.X)
        self._belief_canvas.pack(fill=tk.BOTH, expand=True)
        self._belief_inner = tk.Frame(self._belief_canvas, bg=MNT_BG)
        self._belief_canvas.create_window((0, 0), window=self._belief_inner, anchor='nw')
        self._belief_inner.bind('<Configure>',
            lambda e: self._belief_canvas.configure(
                scrollregion=self._belief_canvas.bbox('all')))

        # --- Separator ---
        tk.Frame(inn, bg=MNT_BDR, height=1).pack(fill=tk.X, pady=(4, 4))

        # --- Phan 2: Duong di (weight=2) ---
        path_hdr = tk.Frame(inn, bg=MNT_BG); path_hdr.pack(fill=tk.X, pady=(0, 2))
        tk.Label(path_hdr, text='Duong Di: Start -> Goal', bg=MNT_BG,
                 fg=MNT_BDR, font=F_HDR).pack(side=tk.LEFT)

        pcf = tk.Frame(inn, bg=MNT_BG); pcf.pack(fill=tk.BOTH, expand=True)
        self._path_canvas = tk.Canvas(pcf, bg=MNT_BG, highlightthickness=0)
        phsb = tk.Scrollbar(pcf, orient=tk.HORIZONTAL, command=self._path_canvas.xview)
        self._path_canvas.configure(xscrollcommand=phsb.set)
        phsb.pack(side=tk.BOTTOM, fill=tk.X)
        self._path_canvas.pack(fill=tk.BOTH, expand=True)
        self._path_inner = tk.Frame(self._path_canvas, bg=MNT_BG)
        self._path_canvas.create_window((0, 0), window=self._path_inner, anchor='nw')
        self._path_inner.bind('<Configure>',
            lambda e: self._path_canvas.configure(
                scrollregion=self._path_canvas.bbox('all')))
        tk.Label(self._path_inner, text='Chua co duong di...',
                 bg=MNT_BG, fg=TXT_DIM, font=F_BODY).pack(padx=20, pady=8)

        # Hien thi trang thai ban dau
        self._render_belief_set(self._start_belief)

    # ─────────────────────────────────────────
    #  RENDER BELIEF SET
    # ─────────────────────────────────────────
    def _render_belief_set(self, belief):
        for w in self._belief_inner.winfo_children():
            w.destroy()
        lst = sorted(belief)
        n   = len(lst)
        self._belief_count_lbl.config(text=f'({n} ma tran)')
        self._lbl_bsiz.config(text=str(n))
        if n == 0:
            tk.Label(self._belief_inner, text='Tap niem tin rong!',
                     bg=MNT_BG, fg=CLR_FAIL, font=F_BODY).pack(padx=20, pady=10)
        else:
            for idx, state in enumerate(lst):
                sf = tk.Frame(self._belief_inner, bg=MNT_BG,
                              highlightbackground=MNT_BDR, highlightthickness=1)
                sf.pack(side=tk.LEFT, padx=5, pady=5, anchor='n')
                tk.Label(sf, text=f'Ma tran {idx+1}', bg=MNT_BG, fg=MNT_BDR,
                         font=F_MINI).pack(pady=(3, 1))
                gf = tk.Frame(sf, bg=MNT_BG); gf.pack(padx=4, pady=(0, 2))
                make_grid(gf, state, MNT_T, MNT_EM, MNT_TXT,
                          font=F_TILE_SM, ipx=7, ipy=4,
                          pad_x=2, pad_y=2)
                if state == GOAL_STATE:
                    lbl = 'GOAL'
                    clr  = CLR_OK
                else:
                    h   = sum(1 for i in range(3) for j in range(3)
                              if state[i][j] != 0 and state[i][j] != GOAL_STATE[i][j])
                    lbl = f'h = {h}'
                    clr  = TXT_MID
                tk.Label(sf, text=lbl, bg=MNT_BG, fg=clr, font=F_MINI).pack(pady=(0, 3))
        self._belief_canvas.update_idletasks()
        self._belief_canvas.configure(scrollregion=self._belief_canvas.bbox('all'))

    # ─────────────────────────────────────────
    #  PATH DISPLAY
    # ─────────────────────────────────────────
    def _clear_path(self):
        for w in self._path_inner.winfo_children():
            w.destroy()

    def _show_path(self, action_seq):
        self._clear_path()
        if not action_seq:
            tk.Label(self._path_inner, text='Da o dich ngay tu dau!',
                     bg=MNT_BG, fg=CLR_OK, font=F_BODY).pack(padx=20, pady=8)
            self._path_canvas.update_idletasks()
            self._path_canvas.configure(scrollregion=self._path_canvas.bbox('all'))
            return

        # Tai hien lai cac buoc
        steps = [self._start_belief]
        cur   = self._start_belief
        for act in action_seq:
            cur = frozenset(move_blank(s, act) for s in cur)
            steps.append(cur)

        for idx, belief_snap in enumerate(steps):
            rep   = sorted(belief_snap)[0]
            n     = len(belief_snap)
            if idx == 0:
                lbl_txt, lbl_clr = 'Start', '#1565C0'
            elif idx == len(steps) - 1:
                lbl_txt, lbl_clr = 'Goal',  CLR_OK
            else:
                lbl_txt, lbl_clr = action_seq[idx - 1], MNT_TXT

            sf = tk.Frame(self._path_inner, bg=MNT_BG)
            sf.pack(side=tk.LEFT, padx=2, pady=4)
            tk.Label(sf, text=lbl_txt, bg=MNT_BG, fg=lbl_clr, font=F_MINI).pack()
            gf = tk.Frame(sf, bg=MNT_BG); gf.pack()
            make_grid(gf, rep, MNT_T, MNT_EM, MNT_TXT,
                      font=F_MINI, ipx=2, ipy=1, pad_x=1, pad_y=1)
            tk.Label(sf, text=f'|B|={n}', bg=MNT_BG, fg=TXT_DIM, font=F_MINI).pack()

            if idx < len(steps) - 1:
                tk.Label(self._path_inner, text='>',
                         bg=MNT_BG, fg=MNT_BDR,
                         font=('Segoe UI', 13, 'bold')).pack(side=tk.LEFT, padx=1)

        self._path_canvas.update_idletasks()
        self._path_canvas.configure(scrollregion=self._path_canvas.bbox('all'))

    # ─────────────────────────────────────────
    #  WIDGET HELPERS
    # ─────────────────────────────────────────
    def _btn(self, parent, text, color, cmd):
        b = tk.Button(parent, text=text, command=cmd, bg=color, fg=TXT_W,
                      font=F_BTN, relief='flat', cursor='hand2',
                      activebackground=color, activeforeground=TXT_W,
                      padx=12, pady=5, bd=0)
        lt = self._lighter(color)
        b.bind('<Enter>', lambda e: b.config(bg=lt))
        b.bind('<Leave>', lambda e: b.config(bg=color))
        return b

    def _badge(self, parent, label, val, clr):
        f = tk.Frame(parent, bg=HDR_BG); f.pack(side=tk.RIGHT, padx=8)
        tk.Label(f, text=label, bg=HDR_BG, fg='#7DD4FC', font=F_STAT).pack()
        lv = tk.Label(f, text=val, bg=HDR_BG, fg=clr, font=F_BDGE); lv.pack()
        return lv

    @staticmethod
    def _lighter(h):
        r, g, b = int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)
        return f'#{min(255,r+40):02x}{min(255,g+40):02x}{min(255,b+40):02x}'

    # ─────────────────────────────────────────
    #  SOLVE
    # ─────────────────────────────────────────
    def _solve(self):
        if self._running:
            return
        self._running = True
        self._action_seq_lbl.config(text='(dang chay...)')
        self._lbl_exp.config(text='0'); self._lbl_stp.config(text='0')
        self._lbl_bsiz.config(text=str(len(self._start_belief)))
        self._clear_path()
        tk.Label(self._path_inner, text='Chua co duong di...',
                 bg=MNT_BG, fg=TXT_DIM, font=F_BODY).pack(padx=20, pady=8)

        self._blf_panel.reset()
        self._blf_panel.set_status('Dang tim kiem...', CLR_WARN)
        self._blf_panel.log_write('[BAT DAU]  Belief-State BFS', 'start')
        self._blf_panel.log_write(
            f'          Tap niem tin: {len(self._start_belief)} ma tran', 'info')
        self._blf_panel.log_write(
            f'          Goal: {[v for r in GOAL_STATE for v in r]}', 'info')
        self._blf_panel.log_write('', '')

        self._render_belief_set(self._start_belief)

        sb = self._start_belief
        threading.Thread(target=belief_state_bfs,
                         args=(sb, GOAL_STATE, self._cb),
                         daemon=True).start()

    # ─────────────────────────────────────────
    #  CALLBACK
    # ─────────────────────────────────────────
    def _cb(self, event, data):
        if event == 'alive':
            return self._running
        elif event == 'belief_step':
            b, p, a = data['belief'], data['path'], data['action']
            s, e, f = data['step'],  data['exp'],   data['frn']
            self.after(0, lambda b=b,p=p,a=a,s=s,e=e,f=f:
                       self._on_step(b, p, a, s, e, f))
        elif event == 'done':
            p, b, e, s = data['path'], data['belief'], data['exp'], data['steps']
            self.after(0, lambda p=p,b=b,e=e,s=s: self._on_done(p, b, e, s))
        elif event == 'fail':
            e = data['exp']
            self.after(0, lambda e=e: self._on_fail(e))
        return None

    def _on_step(self, belief, path, action, step, exp, frn):
        seq = ' -> '.join(path) if path else '(khoi dau)'
        self._action_seq_lbl.config(text=seq)
        self._lbl_exp.config(text=str(exp))
        self._lbl_stp.config(text=str(step))
        self._blf_panel.update_info(len(belief), step, action, exp, frn)
        self._render_belief_set(belief)
        act_str = f"-> '{action}'" if action else '(start)'
        self._blf_panel.log_write(
            f'[#{exp:>4}] Buoc={step} {act_str}  |  belief_size={len(belief)}', 'step')

    def _on_done(self, path, belief, exp, steps):
        self._running = False
        seq = ' -> '.join(path) if path else '(truc tiep)'
        self._action_seq_lbl.config(text=f'OK  {seq}')
        self._lbl_stp.config(text=str(steps))
        self._lbl_exp.config(text=str(exp))
        self._blf_panel.update_info(len(belief), steps,
                                    path[-1] if path else None, exp, 0)
        self._blf_panel.set_status(f'Thanh cong!  {steps} buoc', CLR_OK)
        self._blf_panel.log_write(
            f'\n[XONG]  {steps} buoc — {exp} nodes kham pha', 'done')
        self._blf_panel.log_write(f'       Chuoi: {path}', 'done')
        self._render_belief_set(belief)
        self._show_path(path)
        self._flash_success()

    def _on_fail(self, exp):
        self._running = False
        self._action_seq_lbl.config(text='Khong tim thay!')
        self._blf_panel.set_status('Khong tim thay duong di!', CLR_FAIL)
        self._blf_panel.log_write(
            f'\n[THAT BAI]  {exp} nodes, khong co giai phap.\n', 'fail')
        self._lbl_exp.config(text=str(exp))

    def _flash_success(self, n=6):
        def _f(k):
            if k <= 0:
                self._btn_solve.config(bg=BTN_SOLVE); return
            self._btn_solve.config(bg='#1B5E20' if k % 2 == 0 else BTN_SOLVE)
            self.after(200, lambda: _f(k - 1))
        _f(n)

    # ─────────────────────────────────────────
    #  RESET (random belief)
    # ─────────────────────────────────────────
    def _reset(self):
        self._running = False
        # Sinh tap niem tin ngau nhien moi
        self._start_belief = generate_random_belief(2)

        self._action_seq_lbl.config(text='(chua chay)')
        self._lbl_stp.config(text='—')
        self._lbl_exp.config(text='0')
        self._lbl_bsiz.config(text=str(len(self._start_belief)))

        self._blf_panel.reset()
        self._render_belief_set(self._start_belief)
        self._clear_path()
        tk.Label(self._path_inner, text='Chua co duong di...',
                 bg=MNT_BG, fg=TXT_DIM, font=F_BODY).pack(padx=20, pady=8)

        # Cap nhat cot Initial Belief ben trai
        self._render_init_col()


# ═══════════════════════════════════════════════════════════
if __name__ == '__main__':
    App().mainloop()
