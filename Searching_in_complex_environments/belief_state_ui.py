"""
belief_state_ui.py — Giao dien tich hop 5 thuat toan tim kiem phuc tap
  1. Belief-State BFS          (Start ngau nhien -> 1 Goal co dinh)
  2. No-Obs Multi-Goal BFS     (Start ngau nhien -> Tap nhieu goal)
  3. Partial-Obs Start BFS     (Start theo mask  -> 1 Goal co dinh)
  4. Partial-Obs Goal BFS      (Start ngau nhien -> Goal theo mask)
  5. AND-OR Graph Search       (1 Start -> 1 Goal, moi truong truot)
"""

import random, threading, time, tkinter as tk
from tkinter import ttk
from collections import deque

# ═══════════════════════════════════════════════════════════════════════
#  SHARED CONSTANTS
# ═══════════════════════════════════════════════════════════════════════
ACTIONS = ['U', 'D', 'L', 'R']

# Algo 1, 3 — goal don
GOAL_SINGLE = ((1, 2, 3), (8, 0, 4), (7, 6, 5))

# Algo 2 — tap nhieu goal
GOAL_A = ((1, 2, 3), (8, 0, 4), (7, 6, 5))
GOAL_B = ((1, 2, 3), (4, 5, 6), (7, 8, 0))
GOAL_C = ((8, 7, 6), (5, 4, 3), (2, 1, 0))
GOAL_MULTI = frozenset([GOAL_A, GOAL_B, GOAL_C])

# Algo 3 — mask cho start (o co dinh = gia tri, an = -1)
MASK_START = ((1, 2, -1), (-1, -1, -1), (-1, -1, -1))

# Algo 4 — mask cho goal
MASK_GOAL = ((1, 2, 3), (-1, -1, -1), (7, -1, -1))

# Algo 5 — AND-OR
ANDOR_START = ((1, 2, 3), (4, 0, 5), (7, 8, 6))
ANDOR_GOAL  = ((1, 2, 3), (4, 5, 6), (7, 8, 0))

ALGO_NAMES = [
    'Belief-State BFS',
    'No-Obs Multi-Goal BFS',
    'Partial-Obs Start BFS',
    'Partial-Obs Goal BFS',
    'AND-OR Graph Search',
]


# ═══════════════════════════════════════════════════════════════════════
#  CORE HELPERS
# ═══════════════════════════════════════════════════════════════════════
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


def random_puzzle_state():
    nums = list(range(9))
    random.shuffle(nums)
    return tuple(tuple(nums[i * 3 + j] for j in range(3)) for i in range(3))


def generate_random_belief(n=2, exclude=None):
    """Sinh n trang thai ngau nhien, khac tap exclude."""
    exclude = exclude or set()
    states = []
    while len(states) < n:
        s = random_puzzle_state()
        if s not in exclude and s not in states:
            states.append(s)
    return frozenset(states)


def generate_from_mask(mask, n=2):
    """Algo 3: Sinh n trang thai hop le tu mask (o -1 = an)."""
    fixed = set()
    hidden = []
    for i in range(3):
        for j in range(3):
            if mask[i][j] != -1:
                fixed.add(mask[i][j])
            else:
                hidden.append((i, j))
    remaining = [x for x in range(9) if x not in fixed]
    states = set()
    while len(states) < n:
        r = list(remaining)
        random.shuffle(r)
        tmp = [list(row) for row in mask]
        for k, (ri, ci) in enumerate(hidden):
            tmp[ri][ci] = r[k]
        s = tuple(tuple(row) for row in tmp)
        states.add(s)
    return frozenset(states)


def generate_goal_from_mask(mask, n=3):
    """Algo 4: Sinh n goal tu mask."""
    return generate_from_mask(mask, n)


# ═══════════════════════════════════════════════════════════════════════
#  ALGORITHM 1 & 3: Belief-State BFS (1 goal don)
# ═══════════════════════════════════════════════════════════════════════
def belief_bfs_single_goal(start_belief, goal, cb):
    frontier  = deque([(start_belief, [])])
    explored  = {start_belief}
    nodes_exp = [0]
    while frontier:
        if not cb('alive', {}): return
        cur, path = frontier.popleft()
        nodes_exp[0] += 1
        cb('belief_step', {'belief': cur, 'path': path,
                           'action': path[-1] if path else None,
                           'step': len(path), 'exp': nodes_exp[0], 'frn': len(frontier)})
        time.sleep(0.12)
        if all(s == goal for s in cur):
            cb('done', {'path': path, 'belief': cur,
                        'exp': nodes_exp[0], 'steps': len(path)}); return
        for act in ACTIONS:
            nxt = frozenset(move_blank(s, act) for s in cur)
            if nxt not in explored:
                explored.add(nxt); frontier.append((nxt, path + [act]))
    cb('fail', {'exp': nodes_exp[0]})


# ═══════════════════════════════════════════════════════════════════════
#  ALGORITHM 2: No-Obs Multi-Goal BFS (tap nhieu goal)
# ═══════════════════════════════════════════════════════════════════════
def belief_bfs_multi_goal(start_belief, goal_belief, cb):
    frontier  = deque([(start_belief, [])])
    explored  = {start_belief}
    nodes_exp = [0]
    while frontier:
        if not cb('alive', {}): return
        cur, path = frontier.popleft()
        nodes_exp[0] += 1
        cb('belief_step', {'belief': cur, 'path': path,
                           'action': path[-1] if path else None,
                           'step': len(path), 'exp': nodes_exp[0], 'frn': len(frontier)})
        time.sleep(0.12)
        if cur.issubset(goal_belief):
            cb('done', {'path': path, 'belief': cur,
                        'exp': nodes_exp[0], 'steps': len(path)}); return
        for act in ACTIONS:
            nxt = frozenset(move_blank(s, act) for s in cur)
            if nxt not in explored:
                explored.add(nxt); frontier.append((nxt, path + [act]))
    cb('fail', {'exp': nodes_exp[0]})


# ═══════════════════════════════════════════════════════════════════════
#  ALGORITHM 4: Partial-Obs Goal BFS (goal la tap sinh tu mask)
# ═══════════════════════════════════════════════════════════════════════
def belief_bfs_goal_mask(start_belief, goal_belief, cb):
    """Tuong tu Multi-Goal: goal_belief la frozenset nhieu goal sinh tu mask."""
    belief_bfs_multi_goal(start_belief, goal_belief, cb)


# ═══════════════════════════════════════════════════════════════════════
#  ALGORITHM 5: AND-OR Graph Search
# ═══════════════════════════════════════════════════════════════════════
def get_nondeterministic_results(state, action):
    """Bam 1 nut nhung co the truot sang huong ke."""
    slip = {'U': ['L', 'R'], 'D': ['L', 'R'], 'L': ['U', 'D'], 'R': ['U', 'D']}
    acts = [action] + slip[action]
    return frozenset(move_blank(state, a) for a in acts)


def _or_search(state, goal, path_set, nodes, cb, depth=0):
    if not cb('alive', {}): return 'STOP'
    if state == goal: return 'GOAL_REACHED'
    if state in path_set: return None
    if depth > 30: return None  # gioi han do sau

    nodes[0] += 1
    cb('andor_node', {'state': state, 'depth': depth, 'nodes': nodes[0], 'kind': 'OR'})
    time.sleep(0.04)

    for action in ACTIONS:
        possible = get_nondeterministic_results(state, action)
        plan = _and_search(possible, goal, path_set | {state}, nodes, cb, depth + 1)
        if plan == 'STOP': return 'STOP'
        if plan is not None:
            return {action: plan}
    return None


def _and_search(states, goal, path_set, nodes, cb, depth):
    plan = {}
    for state in states:
        sub = _or_search(state, goal, path_set, nodes, cb, depth)
        if sub == 'STOP': return 'STOP'
        if sub is None: return None
        plan[state] = sub
    return plan


def and_or_search(start_state, goal_state, cb):
    nodes = [0]
    cb('belief_step', {'belief': frozenset([start_state]), 'path': [],
                       'action': None, 'step': 0, 'exp': 0, 'frn': 0})
    plan = _or_search(start_state, goal_state, set(), nodes, cb, 0)
    if plan == 'STOP': return
    if plan is not None:
        cb('andor_done', {'plan': plan, 'exp': nodes[0]})
    else:
        cb('fail', {'exp': nodes[0]})


def format_plan_lines(plan, indent=0):
    """Chuyen cay ke hoach thanh list cac dong text."""
    lines = []
    if plan == 'GOAL_REACHED':
        lines.append('  ' * indent + '-> DAT DICH!')
        return lines
    if plan is None:
        lines.append('  ' * indent + '-> BE TAC')
        return lines
    for action, branches in plan.items():
        lines.append('  ' * indent + f'[Bot bam: {action}]  ({len(branches)} kich ban)')
        for st, sub in branches.items():
            row = [v for r in st for v in r]
            lines.append('  ' * (indent + 1) + f'Kich ban {row}:')
            lines.extend(format_plan_lines(sub, indent + 2))
    return lines


# ═══════════════════════════════════════════════════════════════════════
#  COLORS
# ═══════════════════════════════════════════════════════════════════════
ROOT_BG  = '#F5F7FA'
HDR_BG   = '#1A2E4A';  HDR_LINE = '#3D6A9A'
CB_BG    = '#0F1E2F';  CB_FG    = '#60C8FF'

GOAL_BG  = '#E8F5E9';  GOAL_BDR = '#2E7D32'
GOAL_T   = '#A5D6A7';  GOAL_TXT = '#1B5E20';  GOAL_EM = '#E8F5E9'

INIT_BG  = '#E3F2FD';  INIT_BDR = '#1565C0'
INIT_T   = '#90CAF9';  INIT_TXT = '#0D3B66';  INIT_EM = '#E3F2FD'

MNT_BG   = '#E0F7FA';  MNT_BDR  = '#00838F'
MNT_T    = '#80DEEA';  MNT_TXT  = '#006064';  MNT_EM  = '#E0F7FA'

BLF_BG   = '#EEF6FF';  BLF_BDR  = '#00695C';  BLF_LOG = '#F5FEFF'

ANDOR_BG = '#FFF8E1';  ANDOR_BDR= '#E65100'

TXT_W    = '#FFFFFF';  TXT_DARK = '#1A2440'
TXT_MID  = '#4A6080';  TXT_DIM  = '#90A4B8'
CLR_OK   = '#2E7D32';  CLR_FAIL = '#C62828';  CLR_WARN = '#E65100'
CLR_ALGO = '#1565C0';  CLR_STEPS= '#7B1FA2'
CLR_EXP  = '#00897B';  CLR_FRN  = '#F57F17';  CLR_BSIZ = '#AD1457'
BTN_SOLVE= '#1565C0';  BTN_RESET= '#B71C1C'

F_TTL  = ('Segoe UI', 13, 'bold')
F_HDR  = ('Segoe UI', 11, 'bold')
F_BODY = ('Segoe UI', 10, 'bold')
F_STAT = ('Segoe UI', 10, 'bold')
F_MINI = ('Segoe UI',  9, 'bold')
F_BTN  = ('Segoe UI', 10, 'bold')
F_BDGE = ('Segoe UI', 11, 'bold')
F_MONO = ('Consolas',  9)
F_TILE_LG = ('Segoe UI', 13, 'bold')
F_TILE_SM = ('Segoe UI', 11, 'bold')


# ═══════════════════════════════════════════════════════════════════════
#  GRID HELPER
# ═══════════════════════════════════════════════════════════════════════
def make_grid(parent, state, bg_t, bg_em, fg,
              font=F_TILE_SM, ipx=6, ipy=3, px=2, py=2, mask=None):
    """Ve grid 3x3, tra ve labels[][]."""
    lbls = [[None]*3 for _ in range(3)]
    for i in range(3):
        for j in range(3):
            v = state[i][j]
            hidden = mask and mask[i][j] == -1
            txt  = '?' if hidden else (str(v) if v != 0 else '')
            bgc  = '#BDBDBD' if hidden else (bg_em if v == 0 else bg_t)
            lbl = tk.Label(parent, text=txt, width=2,
                           bg=bgc, fg=fg, font=font, relief='flat',
                           highlightbackground='#B2DFDB', highlightthickness=1)
            lbl.grid(row=i, column=j, padx=px, pady=py, ipadx=ipx, ipady=ipy)
            lbls[i][j] = lbl
    return lbls


# ═══════════════════════════════════════════════════════════════════════
#  RIGHT PANEL
# ═══════════════════════════════════════════════════════════════════════
class InfoPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BLF_BG,
                         highlightbackground=BLF_BDR, highlightthickness=2)
        self._build()

    def _build(self):
        tk.Frame(self, bg=BLF_BDR, height=4).pack(fill=tk.X)
        inn = tk.Frame(self, bg=BLF_BG)
        inn.pack(fill=tk.BOTH, expand=True, padx=14, pady=10)
        tk.Label(inn, text='Thong Tin Thuat Toan',
                 bg=BLF_BG, fg=BLF_BDR, font=F_HDR).pack(anchor='w', pady=(0, 6))

        self._cv = {}
        rows = [
            ('Thuat toan',  '—',                       CLR_ALGO),
            ('Belief Size', 'so ma tran hien tai',     CLR_BSIZ),
            ('Buoc',        'so hanh dong da thuc hien', CLR_STEPS),
            ('Hanh dong',   'lenh vua thuc hien',      '#E65100'),
            ('Nodes KP',    'nodes da kham pha',       CLR_EXP),
            ('Frontier',    'hang doi hien tai',       CLR_FRN),
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

        self._status = tk.Label(inn, text='San sang', bg=BLF_BG,
                                fg=CLR_OK, font=F_HDR)
        self._status.pack(anchor='w', pady=(8, 0))

        tk.Frame(inn, bg=BLF_BDR, height=1).pack(fill=tk.X, pady=(10, 4))
        tk.Label(inn, text='Nhat Ky / Ke Hoach', bg=BLF_BG, fg=BLF_BDR,
                 font=F_HDR).pack(anchor='w', pady=(0, 4))
        lf = tk.Frame(inn, bg=BLF_BG); lf.pack(fill=tk.BOTH, expand=True)
        self._log = tk.Text(lf, bg=BLF_LOG, fg=TXT_DARK, font=F_MONO,
                            relief='flat', wrap=tk.NONE, state=tk.DISABLED,
                            highlightthickness=1, highlightbackground=BLF_BDR)
        vsb = tk.Scrollbar(lf, orient=tk.VERTICAL,   command=self._log.yview)
        hsb = tk.Scrollbar(lf, orient=tk.HORIZONTAL, command=self._log.xview)
        self._log.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self._log.pack(fill=tk.BOTH, expand=True)
        for t, c in [('start','#1565C0'),('step','#006064'),('done','#2E7D32'),
                     ('fail','#C62828'),('info','#AD1457'),('andor','#E65100'),
                     ('plan','#4A148C')]:
            self._log.tag_config(t, foreground=c)

    def set_algo(self, name):
        self._cv['Thuat toan'].config(text=name)

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

    def reset(self, algo_name='—'):
        for k, v in self._cv.items():
            v.config(text='—' if k != 'Thuat toan' else algo_name)
        self._status.config(text='San sang', fg=CLR_OK)
        self.log_clear()


# ═══════════════════════════════════════════════════════════════════════
#  MAIN APP
# ═══════════════════════════════════════════════════════════════════════
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('8-Puzzle — Complex Environment Search')
        self.configure(bg=ROOT_BG)
        self.resizable(True, True)
        self.minsize(1120, 660)

        self._algo_var     = tk.StringVar(value=ALGO_NAMES[0])
        self._running      = False
        self._start_belief = frozenset()
        self._goal_display = None   # cho left-top

        self._build()
        self._on_algo_change()   # khoi tao theo algo mac dinh

    # ─────────────────────────────────────────
    #  BUILD STRUCTURE
    # ─────────────────────────────────────────
    def _build(self):
        self._build_header()
        body = tk.Frame(self, bg=ROOT_BG)
        body.pack(fill=tk.BOTH, expand=True, padx=7, pady=(0, 7))
        body.columnconfigure(0, minsize=510, weight=0)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=3, minsize=240)
        body.rowconfigure(1, weight=4, minsize=330)

        # Left-top: swappable panels
        self._top_host = tk.Frame(body, bg=ROOT_BG)
        self._top_host.grid(row=0, column=0, sticky='nsew', padx=(0, 6), pady=(0, 6))
        self._top_host.rowconfigure(0, weight=1)
        self._top_host.columnconfigure(0, weight=1)

        # Left-bottom: belief set + path
        bot = tk.Frame(body, bg=MNT_BG,
                       highlightbackground=MNT_BDR, highlightthickness=2)
        bot.grid(row=1, column=0, sticky='nsew', padx=(0, 6))
        self._build_bottom(bot)

        # Right panel
        self._info_panel = InfoPanel(body)
        self._info_panel.grid(row=0, column=1, rowspan=2, sticky='nsew')

    # ── Header ─────────────────────────────────────
    def _build_header(self):
        hdr = tk.Frame(self, bg=HDR_BG, height=52)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)

        tk.Label(hdr, text='8-Puzzle Solver', bg=HDR_BG, fg=TXT_W,
                 font=F_TTL).pack(side=tk.LEFT, padx=(14, 4))
        tk.Label(hdr, text='Complex Environments', bg=HDR_BG, fg='#60C8FF',
                 font=F_TTL).pack(side=tk.LEFT, padx=(0, 6))
        tk.Frame(hdr, bg=HDR_LINE, width=1, height=30).pack(side=tk.LEFT, padx=8, pady=10)

        # ComboBox chon thuat toan
        tk.Label(hdr, text='Thuat toan:', bg=HDR_BG, fg='#7DD4FC',
                 font=F_BODY).pack(side=tk.LEFT, padx=(2, 2))
        self._style_combo()
        cb = ttk.Combobox(hdr, textvariable=self._algo_var, values=ALGO_NAMES,
                          state='readonly', font=F_BODY, width=24)
        cb.pack(side=tk.LEFT, pady=10)
        cb.bind('<<ComboboxSelected>>', lambda e: self._on_algo_change())

        tk.Frame(hdr, bg=HDR_LINE, width=1, height=30).pack(side=tk.LEFT, padx=8, pady=10)

        self._btn_solve = self._btn(hdr, 'Giai', BTN_SOLVE, self._solve)
        self._btn_solve.pack(side=tk.LEFT, padx=4)
        self._btn(hdr, 'Reset', BTN_RESET, self._reset).pack(side=tk.LEFT, padx=3)

        sf = tk.Frame(hdr, bg=HDR_BG); sf.pack(side=tk.RIGHT, padx=10)
        self._lbl_stp  = self._badge(sf, 'Steps',      '—', CLR_STEPS)
        self._lbl_bsiz = self._badge(sf, 'Belief Size','—', CLR_BSIZ)
        self._lbl_exp  = self._badge(sf, 'Nodes KP',   '0', CLR_EXP)

    # ── Left-top swappable panels ───────────────────
    def _rebuild_top(self):
        for w in self._top_host.winfo_children():
            w.destroy()
        algo = self._algo_var.get()

        if algo == 'AND-OR Graph Search':
            self._build_top_andor()
        elif algo == 'No-Obs Multi-Goal BFS':
            self._build_top_two_col_multigoal()
        elif algo == 'Partial-Obs Start BFS':
            self._build_top_two_col_mask_start()
        elif algo == 'Partial-Obs Goal BFS':
            self._build_top_two_col_mask_goal()
        else:  # Belief-State BFS
            self._build_top_two_col_single_goal()

    def _build_top_two_col_single_goal(self):
        """2 cot: Goal don | Tap niem tin ban dau."""
        top = tk.Frame(self._top_host, bg=ROOT_BG)
        top.grid(row=0, column=0, sticky='nsew')
        top.columnconfigure(0, weight=1); top.columnconfigure(1, weight=1)
        top.rowconfigure(0, weight=1)
        self._make_goal_col(top, [GOAL_SINGLE], 'Trang Thai Dich', col=0)
        self._make_init_col(top, col=1)

    def _build_top_two_col_multigoal(self):
        """2 cot: Tap 3 goal | Tap niem tin ban dau."""
        top = tk.Frame(self._top_host, bg=ROOT_BG)
        top.grid(row=0, column=0, sticky='nsew')
        top.columnconfigure(0, weight=1); top.columnconfigure(1, weight=1)
        top.rowconfigure(0, weight=1)
        # Left: 3 goal nho
        lf = tk.Frame(top, bg=GOAL_BG,
                      highlightbackground=GOAL_BDR, highlightthickness=2)
        lf.grid(row=0, column=0, sticky='nsew', padx=(0,3), pady=0)
        tk.Frame(lf, bg=GOAL_BDR, height=3).pack(fill=tk.X)
        inn = tk.Frame(lf, bg=GOAL_BG); inn.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)
        tk.Label(inn, text='Tap Trang Thai Dich (3 goal)',
                 bg=GOAL_BG, fg=GOAL_BDR, font=F_HDR).pack()
        tk.Label(inn, text='(issubset: tat ca phai vao tap nay)',
                 bg=GOAL_BG, fg=TXT_MID, font=('Segoe UI',8)).pack(pady=(0,4))
        grow = tk.Frame(inn, bg=GOAL_BG); grow.pack()
        for ci, gs in enumerate([GOAL_A, GOAL_B, GOAL_C]):
            sf = tk.Frame(grow, bg=GOAL_BG); sf.grid(row=0, column=ci, padx=3)
            tk.Label(sf, text=f'Goal {ci+1}', bg=GOAL_BG, fg=GOAL_BDR,
                     font=F_MINI).pack()
            gf = tk.Frame(sf, bg=GOAL_BG); gf.pack()
            make_grid(gf, gs, GOAL_T, GOAL_EM, GOAL_TXT,
                      font=('Segoe UI',8,'bold'), ipx=3, ipy=2)
        self._make_init_col(top, col=1)

    def _build_top_two_col_mask_start(self):
        """2 cot: Goal don | Mask Start + tap sinh ra."""
        top = tk.Frame(self._top_host, bg=ROOT_BG)
        top.grid(row=0, column=0, sticky='nsew')
        top.columnconfigure(0, weight=1); top.columnconfigure(1, weight=1)
        top.rowconfigure(0, weight=1)
        self._make_goal_col(top, [GOAL_SINGLE], 'Trang Thai Dich', col=0)
        # Right: mask + states
        rf = tk.Frame(top, bg=INIT_BG,
                      highlightbackground=INIT_BDR, highlightthickness=2)
        rf.grid(row=0, column=1, sticky='nsew', padx=(3,0))
        tk.Frame(rf, bg=INIT_BDR, height=3).pack(fill=tk.X)
        inn = tk.Frame(rf, bg=INIT_BG); inn.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)
        tk.Label(inn, text='Mask Start (? = an)', bg=INIT_BG, fg=INIT_BDR,
                 font=F_HDR).pack()
        tk.Label(inn, text='(cac o co so co dinh, o ? ngau nhien)',
                 bg=INIT_BG, fg=TXT_MID, font=('Segoe UI',8)).pack(pady=(0,4))
        mf = tk.Frame(inn, bg=INIT_BG); mf.pack()
        make_grid(mf, MASK_START, INIT_T, INIT_EM, INIT_TXT,
                  font=F_TILE_SM, ipx=6, ipy=3, mask=MASK_START)
        tk.Label(inn, text='Tap niem tin ban dau (sinh ngau nhien):',
                 bg=INIT_BG, fg=TXT_MID, font=F_MINI).pack(pady=(6,2))
        self._init_state_frame = tk.Frame(inn, bg=INIT_BG); self._init_state_frame.pack()
        self._render_init_states_in(self._init_state_frame)

    def _build_top_two_col_mask_goal(self):
        """2 cot: Mask Goal | Tap niem tin ban dau."""
        top = tk.Frame(self._top_host, bg=ROOT_BG)
        top.grid(row=0, column=0, sticky='nsew')
        top.columnconfigure(0, weight=1); top.columnconfigure(1, weight=1)
        top.rowconfigure(0, weight=1)
        # Left: mask goal
        lf = tk.Frame(top, bg=GOAL_BG,
                      highlightbackground=GOAL_BDR, highlightthickness=2)
        lf.grid(row=0, column=0, sticky='nsew', padx=(0,3))
        tk.Frame(lf, bg=GOAL_BDR, height=3).pack(fill=tk.X)
        inn = tk.Frame(lf, bg=GOAL_BG); inn.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)
        tk.Label(inn, text='Mask Goal (? = co the)', bg=GOAL_BG, fg=GOAL_BDR,
                 font=F_HDR).pack()
        tk.Label(inn, text='(tap goal duoc sinh tu mask nay)',
                 bg=GOAL_BG, fg=TXT_MID, font=('Segoe UI',8)).pack(pady=(0,4))
        mf = tk.Frame(inn, bg=GOAL_BG); mf.pack()
        make_grid(mf, MASK_GOAL, GOAL_T, GOAL_EM, GOAL_TXT,
                  font=F_TILE_SM, ipx=6, ipy=3, mask=MASK_GOAL)
        tk.Label(inn, text='(Goal set sinh ngau nhien moi lan Reset)',
                 bg=GOAL_BG, fg=TXT_DIM, font=F_MINI).pack(pady=(4,0))
        self._make_init_col(top, col=1)

    def _build_top_andor(self):
        """AND-OR: 2 cot Start | Goal (ca hai don le)."""
        top = tk.Frame(self._top_host, bg=ROOT_BG)
        top.grid(row=0, column=0, sticky='nsew')
        top.columnconfigure(0, weight=1); top.columnconfigure(1, weight=1)
        top.rowconfigure(0, weight=1)
        # Start
        lf = tk.Frame(top, bg=INIT_BG,
                      highlightbackground=INIT_BDR, highlightthickness=2)
        lf.grid(row=0, column=0, sticky='nsew', padx=(0,3))
        tk.Frame(lf, bg=INIT_BDR, height=3).pack(fill=tk.X)
        inn = tk.Frame(lf, bg=INIT_BG); inn.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)
        tk.Label(inn, text='Trang Thai Bat Dau', bg=INIT_BG, fg=INIT_BDR,
                 font=F_HDR).pack()
        tk.Label(inn, text='(moi truong co the truot)', bg=INIT_BG, fg=TXT_MID,
                 font=('Segoe UI',8)).pack(pady=(0,6))
        gf = tk.Frame(inn, bg=INIT_BG); gf.pack()
        make_grid(gf, ANDOR_START, INIT_T, INIT_EM, INIT_TXT,
                  font=F_TILE_LG, ipx=9, ipy=5)
        # Goal
        rf = tk.Frame(top, bg=GOAL_BG,
                      highlightbackground=GOAL_BDR, highlightthickness=2)
        rf.grid(row=0, column=1, sticky='nsew', padx=(3,0))
        tk.Frame(rf, bg=GOAL_BDR, height=3).pack(fill=tk.X)
        inn2 = tk.Frame(rf, bg=GOAL_BG); inn2.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)
        tk.Label(inn2, text='Trang Thai Dich', bg=GOAL_BG, fg=GOAL_BDR,
                 font=F_HDR).pack()
        tk.Label(inn2, text='(AND-OR tim ke hoach du phong)',
                 bg=GOAL_BG, fg=TXT_MID, font=('Segoe UI',8)).pack(pady=(0,6))
        gf2 = tk.Frame(inn2, bg=GOAL_BG); gf2.pack()
        make_grid(gf2, ANDOR_GOAL, GOAL_T, GOAL_EM, GOAL_TXT,
                  font=F_TILE_LG, ipx=9, ipy=5)

    def _make_goal_col(self, parent, goal_list, title, col):
        """Ve cot goal co dinh don le."""
        lf = tk.Frame(parent, bg=GOAL_BG,
                      highlightbackground=GOAL_BDR, highlightthickness=2)
        lf.grid(row=0, column=col, sticky='nsew',
                padx=(0,3) if col == 0 else (3,0))
        tk.Frame(lf, bg=GOAL_BDR, height=3).pack(fill=tk.X)
        inn = tk.Frame(lf, bg=GOAL_BG); inn.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)
        tk.Label(inn, text=title, bg=GOAL_BG, fg=GOAL_BDR, font=F_HDR).pack()
        tk.Label(inn, text='(dich can dat)', bg=GOAL_BG, fg=TXT_MID,
                 font=('Segoe UI',8)).pack(pady=(0,6))
        gf = tk.Frame(inn, bg=GOAL_BG); gf.pack()
        make_grid(gf, goal_list[0], GOAL_T, GOAL_EM, GOAL_TXT,
                  font=F_TILE_LG, ipx=9, ipy=5)

    def _make_init_col(self, parent, col):
        """Ve cot Initial Belief (dong) ben phai."""
        rf = tk.Frame(parent, bg=INIT_BG,
                      highlightbackground=INIT_BDR, highlightthickness=2)
        rf.grid(row=0, column=col, sticky='nsew',
                padx=(3,0) if col == 1 else (0,3))
        tk.Frame(rf, bg=INIT_BDR, height=3).pack(fill=tk.X)
        inn = tk.Frame(rf, bg=INIT_BG); inn.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)
        tk.Label(inn, text='Tap Niem Tin Ban Dau', bg=INIT_BG, fg=INIT_BDR,
                 font=F_HDR).pack()
        n = len(self._start_belief)
        tk.Label(inn, text=f'({n} trang thai ngau nhien)', bg=INIT_BG, fg=TXT_MID,
                 font=('Segoe UI',8)).pack(pady=(0,4))
        self._init_state_frame = tk.Frame(inn, bg=INIT_BG)
        self._init_state_frame.pack()
        self._render_init_states_in(self._init_state_frame)

    def _render_init_states_in(self, parent):
        for w in parent.winfo_children():
            w.destroy()
        for ci, state in enumerate(sorted(self._start_belief)):
            sf = tk.Frame(parent, bg=INIT_BG); sf.grid(row=0, column=ci, padx=5)
            tk.Label(sf, text=f'Trang thai {ci+1}', bg=INIT_BG, fg=INIT_BDR,
                     font=F_MINI).pack(pady=(0,2))
            gf = tk.Frame(sf, bg=INIT_BG); gf.pack()
            make_grid(gf, state, INIT_T, INIT_EM, INIT_TXT,
                      font=F_TILE_SM, ipx=6, ipy=3)

    # ── Bottom panel ─────────────────────────────
    def _build_bottom(self, parent):
        tk.Frame(parent, bg=MNT_BDR, height=3).pack(fill=tk.X)
        inn = tk.Frame(parent, bg=MNT_BG)
        inn.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

        # Belief set hien tai
        bh = tk.Frame(inn, bg=MNT_BG); bh.pack(fill=tk.X, pady=(0,2))
        tk.Label(bh, text='Tap Niem Tin / Trang Thai Hien Tai',
                 bg=MNT_BG, fg=MNT_BDR, font=F_HDR).pack(side=tk.LEFT)
        self._belief_count_lbl = tk.Label(bh, text='', bg=MNT_BG,
                                          fg=CLR_BSIZ, font=F_BODY)
        self._belief_count_lbl.pack(side=tk.LEFT, padx=6)

        sf2 = tk.Frame(inn, bg=MNT_BG); sf2.pack(fill=tk.X, pady=(0,3))
        tk.Label(sf2, text='Chuoi hanh dong:', bg=MNT_BG, fg=TXT_MID,
                 font=F_STAT).pack(side=tk.LEFT)
        self._action_seq_lbl = tk.Label(sf2, text='(chua chay)',
                                        bg=MNT_BG, fg='#E65100', font=F_MONO)
        self._action_seq_lbl.pack(side=tk.LEFT, padx=4)

        bcf = tk.Frame(inn, bg=MNT_BG); bcf.pack(fill=tk.BOTH, expand=True)
        self._belief_canvas = tk.Canvas(bcf, bg=MNT_BG, highlightthickness=0)
        bhsb = tk.Scrollbar(bcf, orient=tk.HORIZONTAL, command=self._belief_canvas.xview)
        self._belief_canvas.configure(xscrollcommand=bhsb.set)
        bhsb.pack(side=tk.BOTTOM, fill=tk.X)
        self._belief_canvas.pack(fill=tk.BOTH, expand=True)
        self._belief_inner = tk.Frame(self._belief_canvas, bg=MNT_BG)
        self._belief_canvas.create_window((0,0), window=self._belief_inner, anchor='nw')
        self._belief_inner.bind('<Configure>',
            lambda e: self._belief_canvas.configure(
                scrollregion=self._belief_canvas.bbox('all')))

        # Duong di
        tk.Frame(inn, bg=MNT_BDR, height=1).pack(fill=tk.X, pady=(4,4))
        ph = tk.Frame(inn, bg=MNT_BG); ph.pack(fill=tk.X, pady=(0,2))
        tk.Label(ph, text='Duong Di / Ke Hoach',
                 bg=MNT_BG, fg=MNT_BDR, font=F_HDR).pack(side=tk.LEFT)
        self._path_hint_lbl = tk.Label(ph, text='',
                                       bg=MNT_BG, fg=TXT_DIM, font=F_MINI)
        self._path_hint_lbl.pack(side=tk.LEFT, padx=6)
        pcf = tk.Frame(inn, bg=MNT_BG); pcf.pack(fill=tk.BOTH, expand=True)
        self._path_canvas = tk.Canvas(pcf, bg=MNT_BG, highlightthickness=0)
        phsb = tk.Scrollbar(pcf, orient=tk.HORIZONTAL, command=self._path_canvas.xview)
        self._path_canvas.configure(xscrollcommand=phsb.set)
        phsb.pack(side=tk.BOTTOM, fill=tk.X)
        self._path_canvas.pack(fill=tk.BOTH, expand=True)
        self._path_inner = tk.Frame(self._path_canvas, bg=MNT_BG)
        self._path_canvas.create_window((0,0), window=self._path_inner, anchor='nw')
        self._path_inner.bind('<Configure>',
            lambda e: self._path_canvas.configure(
                scrollregion=self._path_canvas.bbox('all')))
        tk.Label(self._path_inner, text='Chua co ket qua...',
                 bg=MNT_BG, fg=TXT_DIM, font=F_BODY).pack(padx=20, pady=8)

    # ─────────────────────────────────────────
    #  RENDER BELIEF SET
    # ─────────────────────────────────────────
    def _render_belief_set(self, belief, goal_ref=None):
        for w in self._belief_inner.winfo_children():
            w.destroy()
        lst = sorted(belief)
        n = len(lst)
        self._belief_count_lbl.config(text=f'({n} ma tran)')
        self._lbl_bsiz.config(text=str(n))
        for idx, state in enumerate(lst):
            sf = tk.Frame(self._belief_inner, bg=MNT_BG,
                          highlightbackground=MNT_BDR, highlightthickness=1)
            sf.pack(side=tk.LEFT, padx=5, pady=5, anchor='n')
            tk.Label(sf, text=f'Ma tran {idx+1}', bg=MNT_BG, fg=MNT_BDR,
                     font=F_MINI).pack(pady=(3,1))
            gf = tk.Frame(sf, bg=MNT_BG); gf.pack(padx=4, pady=(0,2))
            make_grid(gf, state, MNT_T, MNT_EM, MNT_TXT,
                      font=F_TILE_SM, ipx=7, ipy=4)
            # Status label
            is_g = False
            if goal_ref:
                if isinstance(goal_ref, frozenset):
                    is_g = state in goal_ref
                else:
                    is_g = (state == goal_ref)
            if is_g:
                lbl, clr = 'GOAL', CLR_OK
            else:
                h = sum(1 for i in range(3) for j in range(3)
                        if state[i][j] != 0 and state[i][j] != GOAL_SINGLE[i][j])
                lbl, clr = f'h={h}', TXT_MID
            tk.Label(sf, text=lbl, bg=MNT_BG, fg=clr, font=F_MINI).pack(pady=(0,3))
        self._belief_canvas.update_idletasks()
        self._belief_canvas.configure(scrollregion=self._belief_canvas.bbox('all'))

    # ─────────────────────────────────────────
    #  PATH DISPLAY
    # ─────────────────────────────────────────
    def _clear_path(self):
        for w in self._path_inner.winfo_children():
            w.destroy()

    def _show_belief_path(self, action_seq, goal_ref=None):
        self._clear_path()
        if not action_seq:
            tk.Label(self._path_inner, text='Da o dich ngay tu dau!',
                     bg=MNT_BG, fg=CLR_OK, font=F_BODY).pack(padx=20, pady=8)
            self._path_canvas.update_idletasks()
            self._path_canvas.configure(scrollregion=self._path_canvas.bbox('all'))
            return
        steps = [self._start_belief]
        cur = self._start_belief
        for act in action_seq:
            cur = frozenset(move_blank(s, act) for s in cur)
            steps.append(cur)
        for idx, bsnap in enumerate(steps):
            rep = sorted(bsnap)[0]
            n   = len(bsnap)
            if idx == 0:       lt, lc = 'Start', '#1565C0'
            elif idx == len(steps)-1: lt, lc = 'Goal', CLR_OK
            else:              lt, lc = action_seq[idx-1], MNT_TXT
            sf = tk.Frame(self._path_inner, bg=MNT_BG); sf.pack(side=tk.LEFT, padx=2, pady=4)
            tk.Label(sf, text=lt, bg=MNT_BG, fg=lc, font=F_MINI).pack()
            gf = tk.Frame(sf, bg=MNT_BG); gf.pack()
            make_grid(gf, rep, MNT_T, MNT_EM, MNT_TXT,
                      font=F_MINI, ipx=2, ipy=1, px=1, py=1)
            tk.Label(sf, text=f'|B|={n}', bg=MNT_BG, fg=TXT_DIM, font=F_MINI).pack()
            if idx < len(steps)-1:
                tk.Label(self._path_inner, text='>',
                         bg=MNT_BG, fg=MNT_BDR,
                         font=('Segoe UI', 13, 'bold')).pack(side=tk.LEFT, padx=1)
        self._path_canvas.update_idletasks()
        self._path_canvas.configure(scrollregion=self._path_canvas.bbox('all'))

    def _show_andor_path(self, plan):
        """Hien thi ke hoach AND-OR duoi dang text don gian."""
        self._clear_path()
        self._path_hint_lbl.config(text='(Ke hoach du phong — xem log chi tiet)')
        lines = format_plan_lines(plan)
        # Hien thi text trong path area
        txt = tk.Text(self._path_inner, bg=MNT_BG, fg=TXT_DARK,
                      font=('Consolas', 8), relief='flat',
                      state=tk.NORMAL, wrap=tk.NONE, height=6)
        txt.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        for ln in lines[:60]:   # gioi han 60 dong
            txt.insert(tk.END, ln + '\n')
        txt.config(state=tk.DISABLED)
        self._path_canvas.update_idletasks()
        self._path_canvas.configure(scrollregion=self._path_canvas.bbox('all'))

    # ─────────────────────────────────────────
    #  ALGO CHANGE
    # ─────────────────────────────────────────
    def _on_algo_change(self):
        self._running = False
        algo = self._algo_var.get()
        # Khoi tao start_belief theo algo
        if algo == 'AND-OR Graph Search':
            self._start_belief = frozenset([ANDOR_START])
            self._goal_ref = ANDOR_GOAL
        elif algo == 'Partial-Obs Start BFS':
            self._start_belief = generate_from_mask(MASK_START, n=2)
            self._goal_ref = GOAL_SINGLE
        elif algo == 'Partial-Obs Goal BFS':
            self._start_belief = generate_random_belief(n=2)
            self._goal_ref = generate_goal_from_mask(MASK_GOAL, n=3)
        elif algo == 'No-Obs Multi-Goal BFS':
            self._start_belief = generate_random_belief(n=2)
            self._goal_ref = GOAL_MULTI
        else:
            self._start_belief = generate_random_belief(n=2)
            self._goal_ref = GOAL_SINGLE

        self._rebuild_top()
        self._render_belief_set(self._start_belief, self._goal_ref)
        self._clear_path()
        tk.Label(self._path_inner, text='Chua co ket qua...',
                 bg=MNT_BG, fg=TXT_DIM, font=F_BODY).pack(padx=20, pady=8)
        self._action_seq_lbl.config(text='(chua chay)')
        self._lbl_stp.config(text='—')
        self._lbl_exp.config(text='0')
        self._info_panel.reset(algo)
        self._path_hint_lbl.config(text='')

    # ─────────────────────────────────────────
    #  SOLVE
    # ─────────────────────────────────────────
    def _solve(self):
        if self._running: return
        self._running = True
        algo = self._algo_var.get()
        self._info_panel.reset(algo)
        self._info_panel.set_status('Dang tim kiem...', CLR_WARN)
        self._info_panel.log_write(f'[BAT DAU]  {algo}', 'start')
        self._clear_path()
        tk.Label(self._path_inner, text='Dang tim...', bg=MNT_BG,
                 fg=TXT_DIM, font=F_BODY).pack(padx=20, pady=8)
        self._action_seq_lbl.config(text='(dang chay...)')
        self._lbl_exp.config(text='0'); self._lbl_stp.config(text='0')
        self._render_belief_set(self._start_belief, self._goal_ref)

        sb = self._start_belief
        gr = self._goal_ref

        if algo == 'AND-OR Graph Search':
            self._info_panel.log_write(
                f'  Start: {[v for r in ANDOR_START for v in r]}', 'info')
            self._info_panel.log_write(
                f'  Goal:  {[v for r in ANDOR_GOAL  for v in r]}', 'info')
            self._info_panel.log_write(
                '  (Moi truong: bam U => co the bi truot L hoac R)', 'info')
            threading.Thread(target=and_or_search,
                             args=(ANDOR_START, ANDOR_GOAL, self._cb),
                             daemon=True).start()
        elif algo == 'No-Obs Multi-Goal BFS':
            self._info_panel.log_write(
                f'  Start belief: {len(sb)} ma tran', 'info')
            self._info_panel.log_write(
                f'  Goal set: {len(gr)} trang thai dich', 'info')
            threading.Thread(target=belief_bfs_multi_goal,
                             args=(sb, gr, self._cb), daemon=True).start()
        elif algo == 'Partial-Obs Goal BFS':
            self._info_panel.log_write(
                f'  Start belief: {len(sb)} ma tran ngau nhien', 'info')
            self._info_panel.log_write(
                f'  Goal set (tu mask): {len(gr)} trang thai', 'info')
            threading.Thread(target=belief_bfs_goal_mask,
                             args=(sb, gr, self._cb), daemon=True).start()
        else:  # Belief-State BFS & Partial-Obs Start BFS
            self._info_panel.log_write(
                f'  Start belief: {len(sb)} ma tran', 'info')
            self._info_panel.log_write(
                f'  Goal: {[v for r in gr for v in r]}', 'info')
            threading.Thread(target=belief_bfs_single_goal,
                             args=(sb, gr, self._cb), daemon=True).start()

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
        elif event == 'andor_node':
            st, d, n, k = data['state'], data['depth'], data['nodes'], data['kind']
            self.after(0, lambda st=st,d=d,n=n,k=k: self._on_andor_node(st,d,n,k))
        elif event == 'done':
            p, b, e, s = data['path'], data['belief'], data['exp'], data['steps']
            self.after(0, lambda p=p,b=b,e=e,s=s: self._on_done(p, b, e, s))
        elif event == 'andor_done':
            plan, e = data['plan'], data['exp']
            self.after(0, lambda pl=plan,e=e: self._on_andor_done(pl, e))
        elif event == 'fail':
            e = data['exp']
            self.after(0, lambda e=e: self._on_fail(e))
        return None

    def _on_step(self, belief, path, action, step, exp, frn):
        seq = ' -> '.join(path) if path else '(khoi dau)'
        self._action_seq_lbl.config(text=seq)
        self._lbl_exp.config(text=str(exp))
        self._lbl_stp.config(text=str(step))
        self._info_panel.update_info(len(belief), step, action, exp, frn)
        self._render_belief_set(belief, self._goal_ref)
        act_s = f"->'{action}'" if action else '(start)'
        self._info_panel.log_write(
            f'[#{exp:>4}] buoc={step} {act_s}  belief_size={len(belief)}', 'step')

    def _on_andor_node(self, state, depth, nodes, kind):
        self._lbl_exp.config(text=str(nodes))
        row = [v for r in state for v in r]
        self._info_panel.log_write(
            f'[{kind}] depth={depth}  nodes={nodes}  state={row}', 'andor')

    def _on_done(self, path, belief, exp, steps):
        self._running = False
        seq = ' -> '.join(path) if path else '(truc tiep)'
        self._action_seq_lbl.config(text=f'OK  {seq}')
        self._lbl_stp.config(text=str(steps))
        self._lbl_exp.config(text=str(exp))
        self._info_panel.update_info(len(belief), steps,
                                     path[-1] if path else None, exp, 0)
        self._info_panel.set_status(f'Thanh cong!  {steps} buoc', CLR_OK)
        self._info_panel.log_write(
            f'\n[XONG]  {steps} buoc — {exp} nodes kham pha', 'done')
        self._info_panel.log_write(f'       Chuoi: {path}', 'done')
        self._render_belief_set(belief, self._goal_ref)
        self._show_belief_path(path, self._goal_ref)
        self._flash_ok()

    def _on_andor_done(self, plan, exp):
        self._running = False
        self._lbl_exp.config(text=str(exp))
        self._lbl_stp.config(text='N/A')
        self._action_seq_lbl.config(text='OK  (Ke hoach du phong)')
        self._info_panel.set_status('Thanh cong!  Tim duoc ke hoach du phong', CLR_OK)
        self._info_panel.log_write(
            f'\n[XONG AND-OR]  {exp} nodes  — Ke hoach du phong:', 'done')
        for ln in format_plan_lines(plan):
            self._info_panel.log_write('  ' + ln, 'plan')
        self._render_belief_set(frozenset([ANDOR_GOAL]), self._goal_ref)
        self._show_andor_path(plan)
        self._flash_ok()

    def _on_fail(self, exp):
        self._running = False
        self._action_seq_lbl.config(text='Khong tim thay!')
        self._info_panel.set_status('Khong tim thay giai phap!', CLR_FAIL)
        self._info_panel.log_write(
            f'\n[THAT BAI]  {exp} nodes, khong co giai phap.\n', 'fail')
        self._lbl_exp.config(text=str(exp))

    def _flash_ok(self, n=6):
        def _f(k):
            if k <= 0:
                self._btn_solve.config(bg=BTN_SOLVE); return
            self._btn_solve.config(bg='#1B5E20' if k%2==0 else BTN_SOLVE)
            self.after(200, lambda: _f(k-1))
        _f(n)

    # ─────────────────────────────────────────
    #  RESET
    # ─────────────────────────────────────────
    def _reset(self):
        self._running = False
        self._on_algo_change()   # sinh lai du lieu moi theo algo hien tai

    # ─────────────────────────────────────────
    #  WIDGET HELPERS
    # ─────────────────────────────────────────
    def _style_combo(self):
        s = ttk.Style(); s.theme_use('default')
        s.configure('TCombobox', fieldbackground=CB_BG, background=CB_BG,
                    foreground=CB_FG, selectbackground=CB_BG,
                    selectforeground=CB_FG, borderwidth=0, arrowcolor=CB_FG)
        s.map('TCombobox',
              fieldbackground=[('readonly', CB_BG)],
              foreground=[('readonly', CB_FG)],
              background=[('readonly', CB_BG)])

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
        r, g, b = int(h[1:3],16), int(h[3:5],16), int(h[5:7],16)
        return f'#{min(255,r+40):02x}{min(255,g+40):02x}{min(255,b+40):02x}'


# ═══════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    App().mainloop()
