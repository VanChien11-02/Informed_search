import copy, heapq, math, tkinter as tk
from tkinter import ttk, messagebox
import threading, time, random

# ═══════════════════════════════════════════════════════════
#  SHARED UTILITIES
# ═══════════════════════════════════════════════════════════

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
    dc = {'U':  0, 'D':  0, 'L': -1, 'R': 1}[a]
    ns = copy.deepcopy(s)
    ns[r][c], ns[r+dr][c+dc] = ns[r+dr][c+dc], ns[r][c]
    return ns

def h_misplaced(s, g):
    """Misplaced tiles — khong ke o trong."""
    return sum(1 for i in range(3) for j in range(3)
               if s[i][j] != 0 and s[i][j] != g[i][j])

def h_manhattan(s, g):
    """Manhattan distance — khong ke o trong."""
    pos = {g[i][j]: (i, j) for i in range(3) for j in range(3)}
    return sum(abs(i - pos[s[i][j]][0]) + abs(j - pos[s[i][j]][1])
               for i in range(3) for j in range(3) if s[i][j] != 0)

def is_solvable(start, goal):
    def inv(s):
        f = [v for row in s for v in row if v != 0]
        return sum(1 for i in range(len(f)) for j in range(i+1, len(f)) if f[i] > f[j])
    return inv(start) % 2 == inv(goal) % 2

def trace_path_dict(node):
    path, n = [], node
    while n: path.append({'state': n['state'], 'action': n['action']}); n = n['parent']
    return list(reversed(path))

def trace_path_obj(node):
    path, n = [], node
    while n is not None:
        path.append({'state': n.state, 'action': n.action})
        n = n.parent
    path.reverse()
    return path

# ═══════════════════════════════════════════════════════════
#  INFORMED SEARCH ALGORITHMS
# ═══════════════════════════════════════════════════════════

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
            cb('done', {'path': trace_path_dict(cur), 'exp': exp, 'frn': len(heap)}); return
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
            cb('done', {'path': trace_path_dict(cur), 'exp': exp, 'frn': len(heap)}); return
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

def idastar_search(start, goal, hfn, cb):
    h0   = hfn(start, goal)
    root = {'state': start, 'parent': None, 'action': None, 'h': h0, 'g': 0, 'f': h0}
    exp  = [0]

    def dfs(node, path_set):
        if not cb('alive', {}): return ('stop', None)
        f = node['f']
        if f > limit: return ('cutoff', f)
        exp[0] += 1
        cb('explore', {'node': node, 'exp': exp[0], 'frn': 0, 'limit': limit})
        time.sleep(0.05)
        if node['state'] == goal: return ('found', trace_path_dict(node))
        min_f = math.inf
        for a in get_actions(node['state']):
            ns = do_move(node['state'], a)
            nt = state_to_tuple(ns)
            if nt in path_set: continue
            g2 = node['g'] + 1; h2 = hfn(ns, goal)
            child = {'state': ns, 'parent': node, 'action': a,
                     'h': h2, 'g': g2, 'f': g2 + h2}
            path_set.add(nt)
            res, val = dfs(child, path_set)
            path_set.discard(nt)
            if res == 'found': return ('found', val)
            if res == 'stop':  return ('stop', None)
            if res == 'cutoff' and val < min_f: min_f = val
        return ('cutoff', min_f) if min_f < math.inf else ('fail', math.inf)

    cur_limit = [h0]
    while True:
        limit = cur_limit[0]
        path_set = {state_to_tuple(start)}
        res, val = dfs(root, path_set)
        if res == 'found': cb('done', {'path': val, 'exp': exp[0], 'frn': 0}); return
        if res == 'stop':  return
        if res == 'fail' or val == math.inf: cb('fail', {'exp': exp[0]}); return
        cur_limit[0] = val

# ═══════════════════════════════════════════════════════════
#  LOCAL SEARCH — Simple Hill Climbing
#  (logic port tu simple_hill_climbing.py: Problem, Node, for...else)
# ═══════════════════════════════════════════════════════════

class SHCProblem:
    def __init__(self, initial, goal):
        self.state = initial
        self.goal  = goal

    def goal_test(self, state): return state == self.goal

    @staticmethod
    def get_blank(state):
        for i in range(3):
            for j in range(3):
                if state[i][j] == 0: return i, j

    def actions(self, state):
        x, y = self.get_blank(state)
        lst = []
        if x < 2: lst.append('D')
        if x > 0: lst.append('U')
        if y < 2: lst.append('R')
        if y > 0: lst.append('L')
        return lst


class SHCNode:
    def __init__(self, state, goal, hfn, parent=None, action=None, step=0):
        self.state  = state
        self.parent = parent
        self.action = action
        self.step   = step
        self._goal  = goal
        self._hfn   = hfn
        self.h_cost = hfn(state, goal)

    def __lt__(self, other): return self.h_cost < other.h_cost


def _shc_child(problem, node, action):
    x, y = problem.get_blank(node.state)
    if   action == 'U': nx, ny = x-1, y
    elif action == 'D': nx, ny = x+1, y
    elif action == 'L': nx, ny = x,   y-1
    else:               nx, ny = x,   y+1
    cs = copy.deepcopy(node.state)
    cs[x][y], cs[nx][ny] = cs[nx][ny], cs[x][y]
    return SHCNode(cs, node._goal, node._hfn, parent=node, action=action, step=node.step+1)


def simple_hc_search(start, goal, hfn, cb):
    """
    Logic goc tu Simple_hill_climbing() trong simple_hill_climbing.py:
        for action in problem.Actions(current.state):
            child = node_child(action)
            if child.h_cost < current.h_cost:
                current = child; break
        else:
            break  # dung: cuc tieu cuc bo hoac goal
    """
    problem = SHCProblem(start, goal)
    current = SHCNode(copy.deepcopy(start), goal, hfn)

    init_hs = [_shc_child(problem, current, a).h_cost
               for a in problem.actions(current.state)]
    cb('shc_step', {'node': current, 'steps': 0, 'neighbors_h': init_hs})
    time.sleep(0.5)

    while True:
        if not cb('alive', {}): return
        moved    = False
        nbr_hs   = []
        for action in problem.actions(current.state):
            child = _shc_child(problem, current, action)
            nbr_hs.append(child.h_cost)
            if child.h_cost < current.h_cost:
                current = child
                moved   = True
                cb('shc_step', {'node': current, 'steps': current.step, 'neighbors_h': nbr_hs})
                time.sleep(0.5)
                break
        if not moved:
            path = trace_path_obj(current)
            if problem.goal_test(current.state):
                cb('done', {'path': path, 'steps': current.step})
            else:
                cb('shc_stuck', {'path': path, 'node': current,
                                 'steps': current.step, 'neighbors_h': nbr_hs})
            return

# ═══════════════════════════════════════════════════════════
#  COLORS — Unified Professional Light Theme
# ═══════════════════════════════════════════════════════════
ROOT_BG  = '#F5F7FA'
HDR_BG   = '#1A2E4A'
HDR_LINE = '#3D6A9A'
CB_BG    = '#0F1E2F'
CB_FG    = '#60C8FF'

# Left-top (boards input)
SKY_BG    = '#E8F4FF';  SKY_BDR   = '#2196F3'
SKY_TILE  = '#90CAF9';  SKY_TXT   = '#0D3B66';  SKY_EMPTY = '#F5F7FA'
GOAL_TILE = '#A5D6A7';  GOAL_TXT  = '#1B5E20';  GOAL_EM   = '#E8F5E9'

# Left-bottom (animated board + path)
MNT_BG    = '#E8FFF6';  MNT_BDR   = '#00897B'
MNT_TILE  = '#80CBC4';  MNT_TXT   = '#004D40';  MNT_EM    = '#E8FFF6'
MNT_ACT   = '#FF8F00'   # highlighted moving tile

# Right panel — Informed Search (indigo)
INF_BG    = '#F0EEFF';  INF_BDR   = '#5C35C8';  INF_LOG   = '#FAF8FF'

# Right panel — Local Search (emerald)
LOC_BG    = '#EEFFF5';  LOC_BDR   = '#1B8A55';  LOC_LOG   = '#F5FFF9'

# Text
TXT_W    = '#FFFFFF';   TXT_DARK  = '#1A2440'
TXT_MID  = '#4A6080';   TXT_DIM   = '#90A4B8'

# Value colors
CLR_H     = '#C62828';  CLR_G     = '#6A1B9A';  CLR_F     = '#E65100'
CLR_LIMIT = '#1565C0';  CLR_ALGO  = '#2E7D32'
CLR_STEPS = '#7B1FA2';  CLR_H_CUR = '#C62828';  CLR_H_NBR = '#E65100'
CLR_OK    = '#2E7D32';  CLR_FAIL  = '#C62828';  CLR_WARN  = '#E65100'
CLR_EXP   = '#00897B';  CLR_FRN   = '#F57F17'

BTN_SOLVE = '#1565C0';  BTN_RAND  = '#6A1B9A';  BTN_RESET = '#B71C1C'

# ═══════════════════════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════════════════════
HEURISTICS = {
    'Misplaced Tiles':    h_misplaced,
    'Manhattan Distance': h_manhattan,
}

SEARCH_TYPES = {
    'Informed Search': [
        'Greedy — Misplaced Tiles',
        'Greedy — Manhattan Distance',
        'A* — Misplaced Tiles',
        'A* — Manhattan Distance',
        'IDA* — Misplaced Tiles',
        'IDA* — Manhattan Distance',
    ],
    'Local Search': [
        'Simple HC — Misplaced Tiles',
        'Simple HC — Manhattan Distance',
    ],
}

# Map algo name -> (fn_key, heur_key)
ALGO_MAP = {
    'Greedy — Misplaced Tiles':       ('greedy',   'misplaced'),
    'Greedy — Manhattan Distance':    ('greedy',   'manhattan'),
    'A* — Misplaced Tiles':           ('astar',    'misplaced'),
    'A* — Manhattan Distance':        ('astar',    'manhattan'),
    'IDA* — Misplaced Tiles':         ('idastar',  'misplaced'),
    'IDA* — Manhattan Distance':      ('idastar',  'manhattan'),
    'Simple HC — Misplaced Tiles':    ('simplehc', 'misplaced'),
    'Simple HC — Manhattan Distance': ('simplehc', 'manhattan'),
}

ALGO_FN = {
    'greedy':   greedy_search,
    'astar':    astar_search,
    'idastar':  idastar_search,
    'simplehc': simple_hc_search,
}

DEFAULT_START = [[2, 1, 4], [7, 0, 6], [5, 3, 8]]
DEFAULT_GOAL  = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]

# ═══════════════════════════════════════════════════════════
#  INFORMED PANEL  (UserControl cho Informed Search)
# ═══════════════════════════════════════════════════════════
class InformedPanel(tk.Frame):
    def __init__(self, parent, F):
        super().__init__(parent, bg=INF_BG,
                         highlightbackground=INF_BDR, highlightthickness=2)
        self._F = F
        self._build()

    def _build(self):
        tk.Frame(self, bg=INF_BDR, height=3).pack(fill=tk.X)
        self._inner = tk.Frame(self, bg=INF_BG)
        self._inner.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)
        inn = self._inner

        tk.Label(inn, text='Informed Search — Thong Tin',
                 bg=INF_BG, fg=INF_BDR, font=self._F['hdr']).pack(anchor='w')

        self._cv = {};  self._dl = {}
        rows = [
            ('h(n)',   '', CLR_H),
            ('g(n)',   '', CLR_G),
            ('f(n)',   '', CLR_F),
            ('limit',  'Nguong f (IDA*)', CLR_LIMIT),
            ('algo',   'Thuat toan',      CLR_ALGO),
        ]
        for key, desc, clr in rows:
            rf = tk.Frame(inn, bg=INF_BG); rf.pack(fill=tk.X, pady=2)
            tk.Label(rf, text=f'{key}:', bg=INF_BG, fg=TXT_MID,
                     font=self._F['stat'], width=7, anchor='w').pack(side=tk.LEFT)
            dl = tk.Label(rf, text=desc, bg=INF_BG, fg=TXT_DIM, font=self._F['stat'])
            dl.pack(side=tk.LEFT)
            self._dl[key] = dl
            v = tk.Label(rf, text='—', bg=INF_BG, fg=clr, font=self._F['bdge'])
            v.pack(side=tk.RIGHT)
            self._cv[key] = v

        self._status = tk.Label(inn, text='San sang', bg=INF_BG, fg=CLR_OK, font=self._F['hdr'])
        self._status.pack(anchor='w', pady=(6, 0))

        tk.Frame(inn, bg=INF_BDR, height=1).pack(fill=tk.X, pady=(10, 4))
        tk.Label(inn, text='Nhat Ky Kham Pha', bg=INF_BG, fg=INF_BDR,
                 font=self._F['hdr']).pack(anchor='w', pady=(0, 4))

        lf = tk.Frame(inn, bg=INF_BG); lf.pack(fill=tk.BOTH, expand=True)
        self._log = tk.Text(lf, bg=INF_LOG, fg=TXT_DARK, font=self._F['mono'],
                            relief='flat', wrap=tk.NONE, state=tk.DISABLED,
                            highlightthickness=1, highlightbackground=INF_BDR)
        vsb = tk.Scrollbar(lf, orient=tk.VERTICAL, command=self._log.yview)
        hsb = tk.Scrollbar(lf, orient=tk.HORIZONTAL, command=self._log.xview)
        self._log.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self._log.pack(fill=tk.BOTH, expand=True)
        self._log.tag_config('explore', foreground='#1565C0')
        self._log.tag_config('done',    foreground='#2E7D32')
        self._log.tag_config('fail',    foreground='#C62828')
        self._log.tag_config('info',    foreground='#6A1B9A')

    # ── Public API ──────────────────────────────
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

    def update_desc(self, algo_type, heur_type):
        h_d = 'Manhattan Distance' if heur_type == 'manhattan' else 'Misplaced Tiles'
        is_g = algo_type in ('astar', 'idastar')
        self._dl['h(n)'].config(text=h_d)
        self._dl['g(n)'].config(text='So buoc thuc te' if is_g else 'Khong dung (Greedy)')
        self._dl['f(n)'].config(text='g(n) + h(n)' if is_g else 'Khong dung (Greedy)')

    def update_costs(self, node, algo_type, limit=None):
        nm = {'greedy': 'Greedy', 'astar': 'A*', 'idastar': 'IDA*'}
        is_g   = algo_type in ('astar', 'idastar')
        is_ida = algo_type == 'idastar'
        if node is None:
            self._cv['h(n)'].config(text='—')
            self._cv['g(n)'].config(text='—' if is_g  else 'N/A')
            self._cv['f(n)'].config(text='—' if is_g  else 'N/A')
            self._cv['limit'].config(text='—' if is_ida else 'N/A')
        else:
            self._cv['h(n)'].config(text=str(node.get('h', '—')))
            self._cv['g(n)'].config(text=str(node.get('g', '—')) if is_g else 'N/A')
            self._cv['f(n)'].config(text=str(node.get('f', '—')) if is_g else 'N/A')
            self._cv['limit'].config(text=str(limit) if is_ida and limit is not None
                                     else ('—' if is_ida else 'N/A'))
        self._cv['algo'].config(text=nm.get(algo_type, '—'))

    def reset(self, algo_type='greedy', heur_type='misplaced'):
        for k in self._cv: self._cv[k].config(text='—')
        self._status.config(text='San sang', fg=CLR_OK)
        self.log_clear()
        self.update_desc(algo_type, heur_type)


# ═══════════════════════════════════════════════════════════
#  LOCAL PANEL  (UserControl cho Local Search)
# ═══════════════════════════════════════════════════════════
class LocalPanel(tk.Frame):
    def __init__(self, parent, F):
        super().__init__(parent, bg=LOC_BG,
                         highlightbackground=LOC_BDR, highlightthickness=2)
        self._F = F
        self._build()

    def _build(self):
        tk.Frame(self, bg=LOC_BDR, height=3).pack(fill=tk.X)
        inn = tk.Frame(self, bg=LOC_BG)
        inn.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

        tk.Label(inn, text='Local Search — Thong Tin',
                 bg=LOC_BG, fg=LOC_BDR, font=self._F['hdr']).pack(anchor='w')

        self._cv = {}
        rows = [
            ('Heuristic',      '',                        '#1565C0'),
            ('h(n) hien tai',  'gia tri h hien tai',      CLR_H_CUR),
            ('h(n) lan truoc', 'h o buoc truoc',          CLR_H_NBR),
            ('h(n) min nbr',   'h nho nhat neighbor',     CLR_H_NBR),
            ('So buoc',        'Buoc thuc te',             CLR_STEPS),
        ]
        for key, desc, clr in rows:
            rf = tk.Frame(inn, bg=LOC_BG); rf.pack(fill=tk.X, pady=2)
            tk.Label(rf, text=f'{key}:', bg=LOC_BG, fg=TXT_MID,
                     font=self._F['stat'], width=16, anchor='w').pack(side=tk.LEFT)
            tk.Label(rf, text=desc, bg=LOC_BG, fg=TXT_DIM,
                     font=self._F['stat']).pack(side=tk.LEFT)
            v = tk.Label(rf, text='—', bg=LOC_BG, fg=clr, font=self._F['bdge'])
            v.pack(side=tk.RIGHT)
            self._cv[key] = v

        self._status = tk.Label(inn, text='San sang', bg=LOC_BG, fg=CLR_OK, font=self._F['hdr'])
        self._status.pack(anchor='w', pady=(6, 0))

        # Algorithm pseudocode box
        tk.Frame(inn, bg=LOC_BDR, height=1).pack(fill=tk.X, pady=(10, 4))
        box = tk.Text(inn, height=5, bg='#F0FFF8', fg=TXT_MID, font=self._F['mono'],
                      relief='flat', wrap=tk.WORD, state=tk.DISABLED,
                      padx=8, pady=6, highlightthickness=1, highlightbackground=LOC_BDR)
        box.pack(fill=tk.X)
        box.config(state=tk.NORMAL)
        box.insert(tk.END,
            "Simple Hill Climbing (logic goc):\n"
            "  for action in Actions(current):\n"
            "      child = node_child(action)\n"
            "      if child.h < current.h:\n"
            "          current = child; break\n"
            "  else: dung (cuc tieu cuc bo / goal)")
        box.config(state=tk.DISABLED)

        tk.Frame(inn, bg=LOC_BDR, height=1).pack(fill=tk.X, pady=(8, 4))
        tk.Label(inn, text='Nhat Ky Tung Buoc', bg=LOC_BG, fg=LOC_BDR,
                 font=self._F['hdr']).pack(anchor='w', pady=(0, 4))

        lf = tk.Frame(inn, bg=LOC_BG); lf.pack(fill=tk.BOTH, expand=True)
        self._log = tk.Text(lf, bg=LOC_LOG, fg=TXT_DARK, font=self._F['mono'],
                            relief='flat', wrap=tk.NONE, state=tk.DISABLED,
                            highlightthickness=1, highlightbackground=LOC_BDR)
        vsb = tk.Scrollbar(lf, orient=tk.VERTICAL, command=self._log.yview)
        hsb = tk.Scrollbar(lf, orient=tk.HORIZONTAL, command=self._log.xview)
        self._log.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self._log.pack(fill=tk.BOTH, expand=True)
        self._log.tag_config('step',  foreground='#1565C0')
        self._log.tag_config('done',  foreground='#2E7D32')
        self._log.tag_config('stuck', foreground='#C62828')
        self._log.tag_config('info',  foreground='#6A1B9A')

    # ── Public API ──────────────────────────────
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

    def update_info(self, h_cur, h_prev, h_nbr_min, steps, heur_name):
        self._cv['h(n) hien tai'].config(text=str(h_cur))
        self._cv['h(n) lan truoc'].config(text=str(h_prev) if h_prev is not None else '—')
        self._cv['h(n) min nbr'].config(text=str(h_nbr_min) if h_nbr_min is not None else '—')
        self._cv['So buoc'].config(text=str(steps))
        self._cv['Heuristic'].config(text=heur_name)

    def reset(self):
        for k in self._cv: self._cv[k].config(text='—')
        self._status.config(text='San sang', fg=CLR_OK)
        self.log_clear()


# ═══════════════════════════════════════════════════════════
#  MAIN APPLICATION
# ═══════════════════════════════════════════════════════════
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('8-Puzzle Solver — Informed & Local Search')
        self.configure(bg=ROOT_BG)
        self.resizable(True, True)
        self.minsize(1040, 610)

        self._start   = copy.deepcopy(DEFAULT_START)
        self._goal    = copy.deepcopy(DEFAULT_GOAL)
        self._cur     = copy.deepcopy(DEFAULT_START)
        self._running = False
        self._prev_h  = None          # for SHC step tracking

        self._type_var = tk.StringVar(value='Informed Search')
        self._algo_var = tk.StringVar()

        self._F = {
            'ttl':  ('Segoe UI', 13, 'bold'),
            'hdr':  ('Segoe UI', 11, 'bold'),
            'tile': ('Segoe UI', 15, 'bold'),
            'big':  ('Segoe UI', 17, 'bold'),
            'mini': ('Segoe UI', 9,  'bold'),
            'btn':  ('Segoe UI', 10, 'bold'),
            'body': ('Segoe UI', 10, 'bold'),
            'mono': ('Consolas', 9),
            'bdge': ('Segoe UI', 11, 'bold'),
            'stat': ('Segoe UI', 10, 'bold'),
        }
        for k, v in self._F.items():
            setattr(self, f'F_{k.upper()}', v)
        self.F_HDR  = self._F['hdr']
        self.F_BODY = self._F['body']
        self.F_BTN  = self._F['btn']
        self.F_TILE = self._F['tile']
        self.F_BIG  = self._F['big']
        self.F_MINI = self._F['mini']
        self.F_BDGE = self._F['bdge']
        self.F_STAT = self._F['stat']
        self.F_MONO = self._F['mono']
        self.F_TTL  = self._F['ttl']

        self._build()
        self._on_type_change()   # populate CB2 and show correct panel

    # ─────────────────────────────────────────
    #  BUILD STRUCTURE
    # ─────────────────────────────────────────
    def _build(self):
        self._build_header()

        body = tk.Frame(self, bg=ROOT_BG)
        body.pack(fill=tk.BOTH, expand=True, padx=7, pady=(0, 7))
        body.columnconfigure(0, minsize=480, weight=0)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=2, minsize=220)
        body.rowconfigure(1, weight=3, minsize=280)

        # Left panels (shared for both search types)
        sky = self._sec(body, SKY_BG, SKY_BDR)
        sky.grid(row=0, column=0, sticky='nsew', padx=(0, 6), pady=(0, 6))
        self._build_sky(sky)

        mnt = self._sec(body, MNT_BG, MNT_BDR)
        mnt.grid(row=1, column=0, sticky='nsew', padx=(0, 6))
        self._build_mint(mnt)

        # Right — swappable panel container
        self._rc = tk.Frame(body, bg=ROOT_BG)
        self._rc.grid(row=0, column=1, rowspan=2, sticky='nsew')
        self._rc.rowconfigure(0, weight=1)
        self._rc.columnconfigure(0, weight=1)

        self._inf_panel = InformedPanel(self._rc, self._F)
        self._loc_panel = LocalPanel(self._rc, self._F)

        self._inf_panel.grid(row=0, column=0, sticky='nsew')
        self._loc_panel.grid(row=0, column=0, sticky='nsew')
        self._loc_panel.grid_remove()   # hidden by default
        self._active_panel = self._inf_panel

    # ─────────────────────────────────────────
    #  HEADER
    # ─────────────────────────────────────────
    def _build_header(self):
        hdr = tk.Frame(self, bg=HDR_BG, height=52)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)

        tk.Label(hdr, text='8-Puzzle Solver',
                 bg=HDR_BG, fg=TXT_W, font=self.F_TTL
                 ).pack(side=tk.LEFT, padx=(14, 8))

        self._vsep(hdr)

        # ComboBox 1 — Loai tim kiem
        tk.Label(hdr, text='Loai:', bg=HDR_BG, fg='#7DD4FC',
                 font=self.F_BODY).pack(side=tk.LEFT, padx=(4, 2))
        self._style_combo()
        cb1 = ttk.Combobox(hdr, textvariable=self._type_var,
                            values=list(SEARCH_TYPES.keys()),
                            state='readonly', font=self.F_BODY, width=13)
        cb1.pack(side=tk.LEFT, pady=10)
        cb1.bind('<<ComboboxSelected>>', lambda e: self._on_type_change())

        # ComboBox 2 — Thuat toan (dynamic)
        tk.Label(hdr, text='Thuat toan:', bg=HDR_BG, fg='#7DD4FC',
                 font=self.F_BODY).pack(side=tk.LEFT, padx=(8, 2))
        self._cb2 = ttk.Combobox(hdr, textvariable=self._algo_var,
                                  state='readonly', font=self.F_BODY, width=26)
        self._cb2.pack(side=tk.LEFT, pady=10)
        self._cb2.bind('<<ComboboxSelected>>', lambda e: self._on_algo_change())

        self._vsep(hdr)

        self._btn_solve = self._btn(hdr, 'Giai',  BTN_SOLVE, self._solve)
        self._btn_solve.pack(side=tk.LEFT, padx=4)
        self._btn(hdr, 'Reset', BTN_RESET, self._reset).pack(side=tk.LEFT, padx=3)

        # Stats (right side) — shared Steps + type-specific
        sf = tk.Frame(hdr, bg=HDR_BG)
        sf.pack(side=tk.RIGHT, padx=10)
        self._lbl_stp = self._badge(sf, 'Steps', '—', CLR_STEPS)

        # Informed-only stats frame
        self._inf_sf = tk.Frame(sf, bg=HDR_BG)
        self._inf_sf.pack(side=tk.RIGHT)
        self._lbl_exp = self._badge(self._inf_sf, 'Explored', '0', CLR_EXP)
        self._lbl_frn = self._badge(self._inf_sf, 'Frontier', '0', CLR_FRN)

        # Local-only stats frame (hidden by default)
        self._loc_sf = tk.Frame(sf, bg=HDR_BG)
        self._lbl_h  = self._badge(self._loc_sf, 'h(n)', '—', CLR_H_CUR)

    # ─────────────────────────────────────────
    #  LEFT — SKY BLUE (boards)
    # ─────────────────────────────────────────
    def _build_sky(self, parent):
        tk.Frame(parent, bg=SKY_BDR, height=3).pack(fill=tk.X)
        inner = tk.Frame(parent, bg=SKY_BG)
        inner.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)
        inner.columnconfigure(0, weight=1)
        inner.columnconfigure(1, weight=1)

        tk.Label(inner, text='Trang Thai Dau', bg=SKY_BG, fg=SKY_BDR,
                 font=self.F_HDR).grid(row=0, column=0, pady=(0, 4))
        tk.Label(inner, text='Trang Thai Dich', bg=SKY_BG, fg='#2E7D32',
                 font=self.F_HDR).grid(row=0, column=1, pady=(0, 4))

        # Start grid (editable)
        self._sv = [[tk.StringVar() for _ in range(3)] for _ in range(3)]
        self._se = [[None]*3 for _ in range(3)]
        sgf = tk.Frame(inner, bg=SKY_BG)
        sgf.grid(row=1, column=0, padx=6, pady=2)
        for i in range(3):
            for j in range(3):
                v = self._start[i][j]
                self._sv[i][j].set('' if v == 0 else str(v))
                e = tk.Entry(sgf, textvariable=self._sv[i][j], width=3,
                             justify='center', font=self.F_TILE,
                             bg=SKY_EMPTY if v == 0 else SKY_TILE,
                             fg=SKY_TXT, insertbackground=TXT_DARK,
                             relief='flat', bd=0,
                             highlightthickness=2,
                             highlightbackground='#BBDEFB',
                             highlightcolor=SKY_BDR)
                e.grid(row=i, column=j, padx=2, pady=2, ipadx=7, ipady=5)
                self._se[i][j] = e

        # Goal grid (display only)
        ggf = tk.Frame(inner, bg=SKY_BG)
        ggf.grid(row=1, column=1, padx=6, pady=2)
        for i in range(3):
            for j in range(3):
                v = self._goal[i][j]
                tk.Label(ggf, text=str(v) if v != 0 else '', width=2,
                         bg=GOAL_EM if v == 0 else GOAL_TILE,
                         fg=GOAL_TXT, font=self.F_TILE, relief='flat',
                         highlightbackground='#C8E6C9', highlightthickness=2
                         ).grid(row=i, column=j, padx=2, pady=2, ipadx=9, ipady=5)

        bf = tk.Frame(inner, bg=SKY_BG)
        bf.grid(row=2, column=0, columnspan=2, pady=(8, 0), sticky='w', padx=6)
        self._btn(bf, 'Ngau Nhien', BTN_RAND, self._randomize).pack(side=tk.LEFT)

    # ─────────────────────────────────────────
    #  LEFT — MINT (animated board + path)
    # ─────────────────────────────────────────
    def _build_mint(self, parent):
        tk.Frame(parent, bg=MNT_BDR, height=3).pack(fill=tk.X)
        inner = tk.Frame(parent, bg=MNT_BG)
        inner.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

        left = tk.Frame(inner, bg=MNT_BG)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 4))
        tk.Label(left, text='Bang Hien Tai', bg=MNT_BG, fg=MNT_BDR,
                 font=self.F_HDR).pack(anchor='w', pady=(0, 4))
        bf = tk.Frame(left, bg=MNT_BG); bf.pack()
        self._ct = [[None]*3 for _ in range(3)]
        for i in range(3):
            for j in range(3):
                v = self._cur[i][j]
                lbl = tk.Label(bf, text=str(v) if v != 0 else '', width=2,
                               bg=MNT_EM if v == 0 else MNT_TILE,
                               fg=MNT_TXT, font=self.F_BIG, relief='flat',
                               highlightbackground='#B2DFDB', highlightthickness=2)
                lbl.grid(row=i, column=j, padx=3, pady=3, ipadx=10, ipady=8)
                self._ct[i][j] = lbl

        tk.Frame(inner, bg=MNT_BDR, width=2).pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=4)

        right = tk.Frame(inner, bg=MNT_BG)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tk.Label(right, text='Duong Di: Start -> Goal', bg=MNT_BG, fg=MNT_BDR,
                 font=self.F_HDR).pack(anchor='w', pady=(0, 4))

        cf = tk.Frame(right, bg=MNT_BG); cf.pack(fill=tk.BOTH, expand=True)
        self._pc = tk.Canvas(cf, bg=MNT_BG, highlightthickness=0)
        hsb = tk.Scrollbar(cf, orient=tk.HORIZONTAL, command=self._pc.xview)
        self._pc.configure(xscrollcommand=hsb.set)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self._pc.pack(fill=tk.BOTH, expand=True)
        self._pi = tk.Frame(self._pc, bg=MNT_BG)
        self._pc.create_window((0, 0), window=self._pi, anchor='nw')
        self._pi.bind('<Configure>', lambda e: self._pc.configure(
            scrollregion=self._pc.bbox('all')))
        tk.Label(self._pi, text='Chua co duong di...',
                 bg=MNT_BG, fg=TXT_DIM, font=self.F_BODY).pack(padx=20, pady=16)

    # ─────────────────────────────────────────
    #  WIDGET HELPERS
    # ─────────────────────────────────────────
    def _sec(self, parent, bg, bdr):
        return tk.Frame(parent, bg=bg, highlightbackground=bdr, highlightthickness=2)

    def _vsep(self, parent):
        tk.Frame(parent, bg=HDR_LINE, width=1, height=30).pack(
            side=tk.LEFT, padx=8, pady=10)

    def _btn(self, parent, text, color, cmd):
        b = tk.Button(parent, text=text, command=cmd, bg=color, fg=TXT_W,
                      font=self.F_BTN, relief='flat', cursor='hand2',
                      activebackground=color, activeforeground=TXT_W,
                      padx=12, pady=5, bd=0)
        lt = self._lighter(color)
        b.bind('<Enter>', lambda e: b.config(bg=lt))
        b.bind('<Leave>', lambda e: b.config(bg=color))
        return b

    def _badge(self, parent, label, val, clr):
        f = tk.Frame(parent, bg=HDR_BG); f.pack(side=tk.RIGHT, padx=8)
        tk.Label(f, text=label, bg=HDR_BG, fg='#7DD4FC', font=self.F_STAT).pack()
        lv = tk.Label(f, text=val, bg=HDR_BG, fg=clr, font=self.F_BDGE); lv.pack()
        return lv

    @staticmethod
    def _lighter(h):
        r, g, b = int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)
        return f'#{min(255,r+40):02x}{min(255,g+40):02x}{min(255,b+40):02x}'

    def _style_combo(self):
        s = ttk.Style(); s.theme_use('default')
        s.configure('TCombobox', fieldbackground=CB_BG, background=CB_BG,
                    foreground=CB_FG, selectbackground=CB_BG,
                    selectforeground=CB_FG, borderwidth=0, arrowcolor=CB_FG)
        s.map('TCombobox',
              fieldbackground=[('readonly', CB_BG)],
              foreground=[('readonly', CB_FG)],
              background=[('readonly', CB_BG)])

    # ─────────────────────────────────────────
    #  BOARD HELPERS
    # ─────────────────────────────────────────
    def _refresh_start_entries(self):
        for i in range(3):
            for j in range(3):
                v = self._start[i][j]
                self._sv[i][j].set('' if v == 0 else str(v))
                self._se[i][j].config(bg=SKY_EMPTY if v == 0 else SKY_TILE)

    def _update_cur_board(self, state, highlight=None):
        for i in range(3):
            for j in range(3):
                v   = state[i][j]
                em  = (v == 0)
                act = (highlight == (i, j))
                bg  = MNT_EM if em else (MNT_ACT if act else MNT_TILE)
                fg  = MNT_TXT if not act else TXT_W
                self._ct[i][j].config(text=str(v) if not em else '', bg=bg, fg=fg)

    def _clear_path(self):
        for w in self._pi.winfo_children(): w.destroy()

    def _show_path(self, path, stuck=False):
        self._clear_path()
        n = len(path)
        for idx, step in enumerate(path):
            st  = step['state']
            act = step.get('action') or 'Start'
            sf  = tk.Frame(self._pi, bg=MNT_BG)
            sf.pack(side=tk.LEFT, padx=3, pady=4)
            if idx == 0:       lt, lc = 'Start',              SKY_BDR
            elif idx == n - 1: lt, lc = ('Stuck' if stuck else 'Goal'), (CLR_FAIL if stuck else CLR_OK)
            else:              lt, lc = str(act),              MNT_TXT
            tk.Label(sf, text=lt, bg=MNT_BG, fg=lc, font=self.F_MINI).pack()
            gf = tk.Frame(sf, bg=MNT_BG); gf.pack()
            for i in range(3):
                for j in range(3):
                    v  = st[i][j]; em = (v == 0)
                    tk.Label(gf, text=str(v) if not em else '', width=2,
                             bg=MNT_EM if em else MNT_TILE, fg=MNT_TXT,
                             font=self.F_MINI, relief='flat',
                             highlightbackground='#B2DFDB', highlightthickness=1
                             ).grid(row=i, column=j, padx=1, pady=1, ipadx=3, ipady=2)
        self._pc.update_idletasks()
        self._pc.configure(scrollregion=self._pc.bbox('all'))

    def _animate(self, path):
        self._running = True
        def step(idx):
            if not self._running or idx >= len(path): return
            st = path[idx]['state']; hi = None
            if idx > 0:
                pv = path[idx-1]['state']
                for i in range(3):
                    for j in range(3):
                        if pv[i][j] != st[i][j] and st[i][j] != 0: hi = (i, j)
            self._update_cur_board(st, hi)
            self.after(400, lambda: step(idx+1))
        step(0)

    def _parse_start_entries(self):
        s, used = [], set()
        for i in range(3):
            row = []
            for j in range(3):
                raw = self._sv[i][j].get().strip()
                if raw == '':       val = 0
                elif raw.isdigit(): val = int(raw)
                else: messagebox.showerror('Loi', f'"{raw}" khong hop le!'); return None
                if val > 8: messagebox.showerror('Loi', f'So {val} > 8!'); return None
                if val in used: messagebox.showerror('Loi', f'So {val} bi trung!'); return None
                used.add(val); row.append(val)
            s.append(row)
        if used != set(range(9)): messagebox.showerror('Loi', 'Can du so 0-8!'); return None
        return s

    # ─────────────────────────────────────────
    #  COMBOBOX CHANGE HANDLERS
    # ─────────────────────────────────────────
    def _on_type_change(self):
        stype = self._type_var.get()
        algos = SEARCH_TYPES[stype]
        self._cb2.config(values=algos)
        self._algo_var.set(algos[0])
        self._swap_panel(stype)
        self._update_stats_visibility(stype)
        self._on_algo_change()

    def _on_algo_change(self):
        algo_name = self._algo_var.get()
        if not algo_name: return
        fn_key, heur_key = ALGO_MAP.get(algo_name, ('greedy', 'misplaced'))
        stype = self._type_var.get()
        if stype == 'Informed Search':
            self._inf_panel.reset(fn_key, heur_key)
        else:
            self._loc_panel.reset()
            self._loc_panel._cv['Heuristic'].config(
                text='Misplaced Tiles' if heur_key == 'misplaced' else 'Manhattan Distance')

    def _swap_panel(self, stype):
        if stype == 'Informed Search':
            self._loc_panel.grid_remove()
            self._inf_panel.grid()
            self._active_panel = self._inf_panel
        else:
            self._inf_panel.grid_remove()
            self._loc_panel.grid()
            self._active_panel = self._loc_panel

    def _update_stats_visibility(self, stype):
        if stype == 'Informed Search':
            self._loc_sf.pack_forget()
            self._inf_sf.pack(side=tk.RIGHT)
        else:
            self._inf_sf.pack_forget()
            self._loc_sf.pack(side=tk.RIGHT)

    # ─────────────────────────────────────────
    #  USER ACTIONS
    # ─────────────────────────────────────────
    def _randomize(self):
        nums = list(range(9)); random.shuffle(nums)
        self._start = [nums[:3], nums[3:6], nums[6:]]
        self._cur   = copy.deepcopy(self._start)
        self._refresh_start_entries()
        self._update_cur_board(self._cur)

    def _reset(self):
        self._running = False
        self._start   = copy.deepcopy(DEFAULT_START)
        self._goal    = copy.deepcopy(DEFAULT_GOAL)
        self._cur     = copy.deepcopy(DEFAULT_START)
        self._prev_h  = None
        self._refresh_start_entries()
        self._update_cur_board(self._cur)
        self._clear_path()
        tk.Label(self._pi, text='Chua co duong di...',
                 bg=MNT_BG, fg=TXT_DIM, font=self.F_BODY).pack(padx=20, pady=16)
        self._lbl_stp.config(text='—')
        self._lbl_frn.config(text='0')
        self._lbl_exp.config(text='0')
        self._lbl_h.config(text='—')
        self._active_panel.set_status('San sang', CLR_OK)
        self._active_panel.log_clear()
        fn_key, heur_key = ALGO_MAP.get(self._algo_var.get(), ('greedy', 'misplaced'))
        if isinstance(self._active_panel, InformedPanel):
            self._active_panel.reset(fn_key, heur_key)
        else:
            self._active_panel.reset()

    # ─────────────────────────────────────────
    #  SOLVE
    # ─────────────────────────────────────────
    def _solve(self):
        if self._running: return
        parsed = self._parse_start_entries()
        if parsed is None: return
        self._start = parsed
        self._cur   = copy.deepcopy(parsed)
        self._prev_h = None
        self._update_cur_board(self._cur)

        if not is_solvable(self._start, self._goal):
            messagebox.showwarning('Khong giai duoc',
                                   'Trang thai khong the giai!\nHay thu Ngau Nhien.')
            return

        algo_name = self._algo_var.get()
        fn_key, heur_key = ALGO_MAP[algo_name]
        hfn = HEURISTICS[
            'Manhattan Distance' if heur_key == 'manhattan' else 'Misplaced Tiles']
        fn  = ALGO_FN[fn_key]

        self._running = True
        self._clear_path()
        self._lbl_stp.config(text='0')
        self._active_panel.log_clear()
        self._active_panel.set_status('Dang chay...', CLR_WARN)
        self._active_panel.log_write(f'[BAT DAU]  {algo_name}', 'info')

        if isinstance(self._active_panel, InformedPanel):
            self._inf_panel.update_costs(None, fn_key)
            self._lbl_frn.config(text='0')
            self._lbl_exp.config(text='0')

        start = copy.deepcopy(self._start)
        goal  = copy.deepcopy(self._goal)
        threading.Thread(target=fn,
                         args=(start, goal, hfn, self._cb),
                         daemon=True).start()

    # ─────────────────────────────────────────
    #  UNIFIED CALLBACK
    # ─────────────────────────────────────────
    def _cb(self, event, data):
        if event == 'alive': return self._running

        # ── Informed Search events ──────────
        if event == 'explore':
            node = data['node']; exp = data['exp']; frn = data['frn']
            lim  = data.get('limit')
            self.after(0, lambda n=node, e=exp, f=frn, l=lim:
                       self._inf_explore(n, e, f, l))
            time.sleep(0.05)

        elif event == 'done':
            path = data['path']; exp = data.get('exp', 0); frn = data.get('frn', 0)
            steps = len(path) - 1
            self.after(0, lambda p=path, e=exp, f=frn, s=steps:
                       self._on_done_inf(p, e, f, s))

        elif event == 'fail':
            exp = data['exp']
            self.after(0, lambda e=exp: self._on_fail_inf(e))

        # ── Local Search events ─────────────
        elif event == 'shc_step':
            node = data['node']; steps = data['steps']; nhs = data['neighbors_h']
            self.after(0, lambda n=node, s=steps, nh=nhs:
                       self._shc_step(n, s, nh))

        elif event == 'shc_stuck':
            path = data['path']; node = data['node']
            steps = data['steps']; nhs = data['neighbors_h']
            self.after(0, lambda p=path, n=node, s=steps, nh=nhs:
                       self._on_shc_stuck(p, n, s, nh))

    # ── Informed handlers ──────────────────
    def _inf_explore(self, node, exp, frn, limit):
        self._update_cur_board(node['state'])
        algo_name = self._algo_var.get()
        fn_key, _ = ALGO_MAP.get(algo_name, ('greedy', 'misplaced'))
        self._inf_panel.update_costs(node, fn_key, limit)
        self._lbl_exp.config(text=str(exp))
        self._lbl_frn.config(text=str(frn))
        self._lbl_stp.config(text=str(exp))
        row = [v for r in node['state'] for v in r]
        msg = f'[#{exp:>4}] {row}  h={node["h"]}'
        if fn_key in ('astar', 'idastar'): msg += f'  g={node["g"]}  f={node["f"]}'
        if fn_key == 'idastar' and limit is not None: msg += f'  lim={limit}'
        self._inf_panel.log_write(msg, 'explore')

    def _on_done_inf(self, path, exp, frn, steps):
        self._running = False
        self._lbl_stp.config(text=str(steps))
        self._lbl_exp.config(text=str(exp))
        self._lbl_frn.config(text=str(frn))
        self._inf_panel.set_status(f'Tim thay!  {steps} buoc', CLR_OK)
        self._inf_panel.log_write(f'\n[XONG]  {steps} buoc — {exp} nodes\n', 'done')
        self._show_path(path)
        self._animate(path)

    def _on_fail_inf(self, exp):
        self._running = False
        self._lbl_exp.config(text=str(exp))
        self._inf_panel.set_status('Khong tim thay duong di!', CLR_FAIL)
        self._inf_panel.log_write(f'\n[THAT BAI]  {exp} nodes, khong co duong di.\n', 'fail')

    # ── Local Search handlers ──────────────
    def _shc_step(self, node, steps, nbrs_h):
        st = node.state; h = node.h_cost
        hi = None
        if steps > 0:
            prev = self._cur
            for i in range(3):
                for j in range(3):
                    if prev[i][j] != st[i][j] and st[i][j] != 0: hi = (i, j)
        self._cur = st
        self._update_cur_board(st, hi)
        h_nbr_min = min(nbrs_h) if nbrs_h else None
        heur_name = ('Misplaced Tiles'
                     if ALGO_MAP.get(self._algo_var.get(), ('', 'misplaced'))[1] == 'misplaced'
                     else 'Manhattan Distance')
        self._loc_panel.update_info(h, self._prev_h, h_nbr_min, steps, heur_name)
        self._lbl_h.config(text=str(h))
        self._lbl_stp.config(text=str(steps))
        act = node.action or 'Start'
        msg = f'[Buoc {steps:>3}]  action={str(act):<2}  h(n)={h}'
        if h_nbr_min is not None: msg += f'  h_nbr_min={h_nbr_min}  delta={h-h_nbr_min:+d}'
        self._loc_panel.log_write(msg, 'step')
        self._prev_h = h

    def _on_shc_stuck(self, path, node, steps, nbrs_h):
        self._running = False
        h = node.h_cost
        self._lbl_stp.config(text=str(steps))
        self._loc_panel.set_status(f'Ket cuc bo!  h={h}  ({steps} buoc)', CLR_FAIL)
        nbr_str = str(sorted(nbrs_h)) if nbrs_h else '[]'
        self._loc_panel.log_write(
            f'\n[KET]  Cuc tieu cuc bo — h={h}\n'
            f'       Neighbors: {nbr_str}\n'
            f'       Khong co neighbor nao co h < {h}.\n', 'stuck')
        self._show_path(path, stuck=True)
        self._animate(path)


# ═══════════════════════════════════════════════════════════
if __name__ == '__main__':
    App().mainloop()
