import copy, heapq, math, tkinter as tk
from tkinter import ttk, messagebox
import threading, time, random

def random_start_state():
    nums  = list(range(9))
    random.shuffle(nums)
    start= [nums[0:3], nums[3:6], nums[6:9]]
    return start

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

def trace_path_obj0(node):
    """Trace path for nodes where parent sentinel is 0 (not None)."""
    path, n = [], node
    while n != 0 and n is not None:
        path.append({'state': n.state, 'action': n.action})
        n = n.parent
    path.reverse()
    return path

# ═══════════════════════════════════════════════════════════
#  UNINFORMED SEARCH ALGORITHMS
# ═══════════════════════════════════════════════════════════

def bfs_search(start, goal, hfn, cb):
    """BFS — Breadth-First Search (port tu BFS.py)."""
    from collections import deque
    root = {'state': start, 'parent': None, 'action': None, 'g': 0}
    if start == goal:
        cb('done', {'path': [{'state': start, 'action': None}], 'exp': 0, 'frn': 0}); return
    frontier = deque([root])
    frontier_set = {state_to_tuple(start)}
    explored = set()
    exp = 0
    while frontier:
        if not cb('alive', {}): return
        cur = frontier.popleft()
        ct  = state_to_tuple(cur['state'])
        frontier_set.discard(ct)
        explored.add(ct); exp += 1
        cb('unf_explore', {'node': cur, 'exp': exp, 'frn': len(frontier), 'algo': 'BFS'})
        time.sleep(0.02)
        for a in get_actions(cur['state']):
            ns = do_move(cur['state'], a)
            nt = state_to_tuple(ns)
            if nt not in explored and nt not in frontier_set:
                child = {'state': ns, 'parent': cur, 'action': a, 'g': cur['g']+1}
                if ns == goal:
                    cb('done', {'path': trace_path_dict(child),
                                'exp': exp, 'frn': len(frontier)}); return
                frontier.append(child)
                frontier_set.add(nt)
    cb('fail', {'exp': exp})


def dfs_search(start, goal, hfn, cb):
    """DFS — Depth-First Search (port tu DFS.py, stack-based, cycle check)."""
    root = {'state': start, 'parent': None, 'action': None, 'g': 0}
    frontier = [root]
    frontier_set = {state_to_tuple(start)}
    explored = set()
    exp = 0
    while frontier:
        if not cb('alive', {}): return
        cur = frontier.pop()
        ct  = state_to_tuple(cur['state'])
        frontier_set.discard(ct)
        if ct in explored: continue
        explored.add(ct); exp += 1
        cb('unf_explore', {'node': cur, 'exp': exp, 'frn': len(frontier), 'algo': 'DFS'})
        time.sleep(0.02)
        if cur['state'] == goal:
            cb('done', {'path': trace_path_dict(cur),
                        'exp': exp, 'frn': len(frontier)}); return
        for a in get_actions(cur['state']):
            ns = do_move(cur['state'], a)
            nt = state_to_tuple(ns)
            if nt not in explored and nt not in frontier_set:
                child = {'state': ns, 'parent': cur, 'action': a, 'g': cur['g']+1}
                frontier.append(child)
                frontier_set.add(nt)
    cb('fail', {'exp': exp})


def ids_search(start, goal, hfn, cb):
    """IDS — Iterative Deepening Search (port tu iteraive_deepening_search.py)."""
    exp_total = [0]
    depth = 0

    def depth_limited(problem_state, limit):
        root = {'state': problem_state, 'parent': None, 'action': None, 'g': 0}
        frontier = [root]
        explored = {state_to_tuple(root['state']): 0}
        cutoff_occurred = False
        while frontier:
            if not cb('alive', {}): return 'stop', None
            cur = frontier.pop()
            ct  = state_to_tuple(cur['state'])
            exp_total[0] += 1
            cb('unf_explore', {'node': cur, 'exp': exp_total[0],
                               'frn': len(frontier), 'algo': 'IDS',
                               'depth': cur['g'], 'limit': limit})
            time.sleep(0.02)
            if cur['state'] == goal:
                return 'found', trace_path_dict(cur)
            if cur['g'] >= limit:
                cutoff_occurred = True
                continue
            for a in get_actions(cur['state']):
                ns  = do_move(cur['state'], a)
                nt  = state_to_tuple(ns)
                ng  = cur['g'] + 1
                if nt not in explored or ng < explored[nt]:
                    explored[nt] = ng
                    child = {'state': ns, 'parent': cur, 'action': a, 'g': ng}
                    frontier.append(child)
        return ('cutoff', None) if cutoff_occurred else ('fail', None)

    while True:
        res, val = depth_limited(start, depth)
        if res == 'found':
            cb('done', {'path': val, 'exp': exp_total[0], 'frn': 0,
                        'depth': depth}); return
        if res == 'stop': return
        if res == 'fail':
            cb('fail', {'exp': exp_total[0]}); return
        depth += 1


def ucs_search(start, goal, hfn, cb):
    """UCS — Uniform Cost Search (port tu UCS.py).
    Trong 8-puzzle moi buoc co cost = 1 nen UCS tuong duong BFS,
    nhung van dung priority queue theo path_cost."""
    root = {'state': start, 'parent': None, 'action': None, 'g': 0}
    heap = [(0, 0, root)]
    best = {state_to_tuple(start): 0}
    cnt  = 0; exp = 0
    while heap:
        if not cb('alive', {}): return
        cost, _, cur = heapq.heappop(heap)
        ct = state_to_tuple(cur['state'])
        if cost > best.get(ct, math.inf): continue   # outdated entry
        exp += 1
        cb('unf_explore', {'node': cur, 'exp': exp, 'frn': len(heap),
                           'algo': 'UCS', 'cost': cur['g']})
        time.sleep(0.02)
        if cur['state'] == goal:
            cb('done', {'path': trace_path_dict(cur),
                        'exp': exp, 'frn': len(heap)}); return
        for a in get_actions(cur['state']):
            ns  = do_move(cur['state'], a)
            nt  = state_to_tuple(ns)
            ng  = cur['g'] + 1
            if nt not in best or ng < best[nt]:
                best[nt] = ng; cnt += 1
                child = {'state': ns, 'parent': cur, 'action': a, 'g': ng}
                heapq.heappush(heap, (ng, cnt, child))
    cb('fail', {'exp': exp})


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
#  LOCAL SEARCH — Shared Node class (supports both heuristics)
# ═══════════════════════════════════════════════════════════

class LSProblem:
    """Shared problem class cho tat ca Local Search algorithms."""
    def __init__(self, initial, goal):
        self.state = initial
        self.goal  = goal

    def goal_test(self, state): return state == self.goal

    @staticmethod
    def getLocationNull(state):
        for i in range(3):
            for j in range(3):
                if state[i][j] == 0: return i, j
        return None

    def Actions(self, state):
        x, y = self.getLocationNull(state)
        lst = []
        if x < 2: lst.append('D')
        if x > 0: lst.append('U')
        if y < 2: lst.append('R')
        if y > 0: lst.append('L')
        return lst


class LSNode:
    """Node for Local Search with pluggable heuristic."""
    def __init__(self, state, goal, hfn, parent=0, action="", step=0):
        self.state  = state
        self.parent = parent
        self.action = action
        self.step   = step
        self._goal  = goal
        self._hfn   = hfn
        self.h_cost = hfn(state, goal)

    def __lt__(self, other): return self.h_cost < other.h_cost


def _ls_child(problem, node, action):
    x, y = problem.getLocationNull(node.state)
    if   action == 'U': nx, ny = x-1, y
    elif action == 'D': nx, ny = x+1, y
    elif action == 'L': nx, ny = x,   y-1
    else:               nx, ny = x,   y+1
    cs = copy.deepcopy(node.state)
    cs[x][y], cs[nx][ny] = cs[nx][ny], cs[x][y]
    return LSNode(cs, node._goal, node._hfn, parent=node, action=action, step=node.step+1)


# ─── Simple Hill Climbing ─────────────────────────────────

# SHC classes kept as aliases for backward compat
SHCProblem = LSProblem

class SHCNode(LSNode):
    pass

def _shc_child(problem, node, action):
    return _ls_child(problem, node, action)


def simple_hc_search(start, goal, hfn, cb):
    """
    Logic goc tu Simple_hill_climbing():
        for action in Actions(current):
            child = node_child(action)
            if child.h <= current.h: current = child; break
        else: dung
    """
    problem = LSProblem(start, goal)
    current = LSNode(copy.deepcopy(start), goal, hfn)

    init_hs = [_ls_child(problem, current, a).h_cost
               for a in problem.Actions(current.state)]
    cb('shc_step', {'node': current, 'steps': 0, 'neighbors_h': init_hs})
    time.sleep(0.5)

    while True:
        if not cb('alive', {}): return
        moved  = False
        nbr_hs = []
        for action in problem.Actions(current.state):
            child = _ls_child(problem, current, action)
            nbr_hs.append(child.h_cost)
            if child.h_cost <= current.h_cost:
                current = child
                moved   = True
                cb('shc_step', {'node': current, 'steps': current.step, 'neighbors_h': nbr_hs})
                time.sleep(0.5)
                break
        if not moved:
            path = trace_path_obj0(current)
            if problem.goal_test(current.state):
                cb('done', {'path': path, 'steps': current.step})
            else:
                cb('shc_stuck', {'path': path, 'node': current,
                                 'steps': current.step, 'neighbors_h': nbr_hs})
            return


# ─── Steepest Ascent Hill Climbing ───────────────────────
# Logic port tu Steepest_ascent_hill_climbing.py:
#   chon neighbor tot nhat (h nho nhat) trong tat ca neighbors

def steepest_ascent_hc_search(start, goal, hfn, cb):
    """
    Steepest Ascent HC: xet TAT CA neighbors, chon neighbor
    co h nho nhat. Dung khi khong co neighbor nao tot hon.
    """
    problem = LSProblem(start, goal)
    current = LSNode(copy.deepcopy(start), goal, hfn)

    nbr_hs_init = [_ls_child(problem, current, a).h_cost
                   for a in problem.Actions(current.state)]
    cb('loc_step', {'node': current, 'steps': 0, 'neighbors_h': nbr_hs_init,
                    'algo': 'Steepest HC'})
    time.sleep(0.5)

    while True:
        if not cb('alive', {}): return
        better_neighbors = []
        nbr_hs = []
        for action in problem.Actions(current.state):
            neighbor = _ls_child(problem, current, action)
            nbr_hs.append(neighbor.h_cost)
            if neighbor.h_cost <= current.h_cost:
                heapq.heappush(better_neighbors, (neighbor.h_cost, neighbor))

        if len(better_neighbors) == 0:
            path = trace_path_obj0(current)
            if problem.goal_test(current.state):
                cb('done', {'path': path, 'steps': current.step})
            else:
                cb('shc_stuck', {'path': path, 'node': current,
                                 'steps': current.step, 'neighbors_h': nbr_hs})
            return
        else:
            _, best_neighbor = heapq.heappop(better_neighbors)
            current = best_neighbor
            nbr_hs_cur = [_ls_child(problem, current, a).h_cost
                          for a in problem.Actions(current.state)]
            cb('loc_step', {'node': current, 'steps': current.step,
                            'neighbors_h': nbr_hs_cur, 'algo': 'Steepest HC'})
            time.sleep(0.5)


# ─── Stochastic Hill Climbing ────────────────────────────
# Logic port tu Stochastic_hill_climbing.py:
#   random.choice trong so cac neighbor tot hon

def stochastic_hc_search(start, goal, hfn, cb):
    """
    Stochastic HC: chon NGAU NHIEN mot neighbor co h <= h hien tai.
    """
    problem = LSProblem(start, goal)
    current = LSNode(copy.deepcopy(start), goal, hfn)

    nbr_hs_init = [_ls_child(problem, current, a).h_cost
                   for a in problem.Actions(current.state)]
    cb('loc_step', {'node': current, 'steps': 0, 'neighbors_h': nbr_hs_init,
                    'algo': 'Stochastic HC'})
    time.sleep(0.5)

    while True:
        if not cb('alive', {}): return
        better_neighbors = []
        nbr_hs = []
        for action in problem.Actions(current.state):
            neighbor = _ls_child(problem, current, action)
            nbr_hs.append(neighbor.h_cost)
            if neighbor.h_cost <= current.h_cost:
                better_neighbors.append(neighbor)

        if len(better_neighbors) == 0:
            path = trace_path_obj0(current)
            if problem.goal_test(current.state):
                cb('done', {'path': path, 'steps': current.step})
            else:
                cb('shc_stuck', {'path': path, 'node': current,
                                 'steps': current.step, 'neighbors_h': nbr_hs})
            return

        next_state = random.choice(better_neighbors)
        current = next_state
        nbr_hs_cur = [_ls_child(problem, current, a).h_cost
                      for a in problem.Actions(current.state)]
        cb('loc_step', {'node': current, 'steps': current.step,
                        'neighbors_h': nbr_hs_cur, 'algo': 'Stochastic HC'})
        time.sleep(0.5)


# ─── Random Restart Hill Climbing ────────────────────────
# Logic port tu Random_restart_hill_climbing.py:
#   thu nhieu lan tu cac trang thai ngau nhien khac nhau

def random_restart_hc_search(start, goal, hfn, cb):
    """
    Random Restart HC: neu bi ket thi khoi dong lai
    tu mot trang thai ngau nhien khac (toi da max_restart lan).
    """
    MAX_RESTART = 10
    problem = LSProblem(start, goal)

    for restart_idx in range(MAX_RESTART):
        if restart_idx == 0:
            init_state = copy.deepcopy(start)
        else:
            # Khoi dong lai tu trang thai ngau nhien hop le
            nums = list(range(9))
            while True:
                random.shuffle(nums)
                ns = [nums[:3], nums[3:6], nums[6:]]
                if is_solvable(ns, goal):
                    init_state = ns
                    break

        current = LSNode(copy.deepcopy(init_state), goal, hfn)
        choice_visited = set()
        choice_visited.add(state_to_tuple(current.state))

        cb('rrhc_restart', {'node': current, 'restart': restart_idx,
                            'steps': current.step})
        time.sleep(0.3)

        while True:
            if not cb('alive', {}): return
            if problem.goal_test(current.state):
                path = trace_path_obj0(current)
                cb('done', {'path': path, 'steps': current.step,
                            'restarts': restart_idx})
                return

            better_neighbors = []
            nbr_hs = []
            for action in problem.Actions(current.state):
                neighbor = _ls_child(problem, current, action)
                nt = state_to_tuple(neighbor.state)
                nbr_hs.append(neighbor.h_cost)
                if neighbor.h_cost <= current.h_cost and nt not in choice_visited:
                    better_neighbors.append(neighbor)

            if len(better_neighbors) == 0:
                # Ket cuc bo, restart
                cb('rrhc_local_stuck', {'node': current, 'restart': restart_idx,
                                        'steps': current.step, 'neighbors_h': nbr_hs})
                time.sleep(0.3)
                break

            next_state = random.choice(better_neighbors)
            choice_visited.add(state_to_tuple(next_state.state))
            current = next_state
            nbr_hs_cur = [_ls_child(problem, current, a).h_cost
                          for a in problem.Actions(current.state)]
            cb('loc_step', {'node': current, 'steps': current.step,
                            'neighbors_h': nbr_hs_cur, 'algo': 'Random Restart HC'})
            time.sleep(0.4)

    # Het luot restart — that bai
    cb('rrhc_fail', {'restarts': MAX_RESTART})


# ─── Local Beam Search ───────────────────────────────────
# Logic port tu local_beam_search.py:
#   giu k trang thai tot nhat qua moi vong lap

def local_beam_search_fn(start, goal, hfn, cb, k=3):
    """
    Local Beam Search: giu k trang thai tot nhat moi vong.
    k lay tu BEAM_K_VAR neu co, mac dinh k=3.
    """
    problem = LSProblem(start, goal)
    start_node = LSNode(copy.deepcopy(start), goal, hfn)
    current_set = [start_node]
    max_iterations = 1000

    cb('beam_init', {'nodes': current_set, 'k': k, 'iteration': 0})
    time.sleep(0.3)

    for iteration in range(max_iterations):
        if not cb('alive', {}): return

        neighbor_states = set()
        neighbor_pqueue = []

        for node in current_set:
            for action in problem.Actions(node.state):
                neighbor = _ls_child(problem, node, action)
                nt = state_to_tuple(neighbor.state)
                if nt not in neighbor_states:
                    neighbor_states.add(nt)
                    if problem.goal_test(neighbor.state):
                        path = trace_path_obj0(neighbor)
                        cb('done', {'path': path, 'steps': neighbor.step,
                                    'iterations': iteration + 1})
                        return
                    heapq.heappush(neighbor_pqueue, (neighbor.h_cost, neighbor))

        if len(neighbor_pqueue) == 0:
            cb('beam_fail', {'iteration': iteration})
            return

        # Chon k trang thai tot nhat
        new_set = []
        while len(new_set) < k and len(neighbor_pqueue) > 0:
            _, node = heapq.heappop(neighbor_pqueue)
            new_set.append(node)

        current_set = new_set
        h_vals = [n.h_cost for n in current_set]

        cb('beam_step', {'nodes': current_set, 'k': k,
                         'iteration': iteration + 1, 'h_vals': h_vals})
        time.sleep(0.4)

    cb('beam_fail', {'iteration': max_iterations})


def simulated_annealing_search(start, goal, hfn, cb):
    """
    Simulated Annealing — port tu simulated_annealing.py.
    T: nhiet do ban dau, lam nguoi theo ty le alpha moi buoc.
    """
    problem = LSProblem(start, goal)
    current = LSNode(copy.deepcopy(start), goal, hfn)
    T       = 100.0
    T_min   = 0.5
    alpha   = 0.97     # cooling rate
    steps   = 0

    while T > T_min:
        if not cb('alive', {}): return
        h_cur = current.h_cost

        if problem.goal_test(current.state):
            path = trace_path_obj0(current)
            cb('done', {'path': path, 'steps': steps})
            return

        actions  = problem.Actions(current.state)
        if not actions:
            break
        action   = random.choice(actions)
        neighbor = _ls_child(problem, current, action)
        delta    = neighbor.h_cost - h_cur   # delta > 0 = worse

        if delta < 0:
            accepted = True
        else:
            p        = math.exp(-delta / T) if T > 0 else 0
            accepted = random.random() < p

        nbrs_h = [_ls_child(problem, current, a).h_cost
                  for a in problem.Actions(current.state)]

        cb('sa_step', {
            'node':     current,
            'steps':    steps,
            'T':        round(T, 3),
            'delta':    delta,
            'accepted': accepted,
            'neighbor': neighbor,
            'neighbors_h': nbrs_h,
        })
        time.sleep(0.08)

        if accepted:
            current = neighbor
            steps  += 1

        T *= alpha

    # Het nhiet ma chua den dich
    if problem.goal_test(current.state):
        path = trace_path_obj0(current)
        cb('done', {'path': path, 'steps': steps})
    else:
        path = trace_path_obj0(current)
        cb('sa_frozen', {
            'path':  path,
            'node':  current,
            'steps': steps,
            'T':     round(T, 4),
        })


def find_min_distance(start, goal):
    from collections import deque
    if start == goal:
        return 0
    st_t = state_to_tuple(start)
    g_t = state_to_tuple(goal)
    q = deque([(st_t, 0)])
    visited = {st_t}
    while q:
        curr, dist = q.popleft()
        if curr == g_t:
            return dist
        curr_lst = [list(row) for row in curr]
        for act in get_actions(curr_lst):
            ns = do_move(curr_lst, act)
            nst = state_to_tuple(ns)
            if nst not in visited:
                visited.add(nst)
                q.append((nst, dist + 1))
    return -1


def backtracking_search(start, goal, hfn, cb):
    visited = {state_to_tuple(start)}
    root = {'state': start, 'parent': None, 'action': None, 'g': 0}
    exp_count = [0]

    def backtrack(cur_node, depth_limit):
        if not cb('alive', {}):
            return None

        cur_state = cur_node['state']
        exp_count[0] += 1

        cb('csp_explore', {
            'node': cur_node,
            'exp': exp_count[0],
            'frn': depth_limit - cur_node['g'],
            'algo': 'Backtracking Search',
            'depth': cur_node['g']
        })
        time.sleep(0.04)

        if cur_state == goal:
            return cur_node

        if cur_node['g'] >= depth_limit:
            return None

        for action in get_actions(cur_state):
            next_state = do_move(cur_state, action)
            next_tuple = state_to_tuple(next_state)
            if next_tuple not in visited:
                visited.add(next_tuple)
                child_node = {
                    'state': next_state,
                    'parent': cur_node,
                    'action': action,
                    'g': cur_node['g'] + 1
                }
                res = backtrack(child_node, depth_limit)
                if res is not None:
                    return res
                visited.remove(next_tuple)
        return None

    sol_node = backtrack(root, depth_limit=20)
    if sol_node:
        path_list = trace_path_dict(sol_node)
        cb('done', {'path': path_list, 'exp': exp_count[0], 'frn': 0, 'steps': len(path_list)-1})
    else:
        cb('fail', {'exp': exp_count[0]})


def forward_checking_search(start, goal, hfn, cb):
    visited = {state_to_tuple(start)}
    root = {'state': start, 'parent': None, 'action': None, 'g': 0}
    exp_count = [0]

    def forward_check_fn(state):
        for action in get_actions(state):
            ns = do_move(state, action)
            if state_to_tuple(ns) not in visited:
                return True
        return False

    def backtrack(cur_node, depth_limit):
        if not cb('alive', {}):
            return None

        cur_state = cur_node['state']
        exp_count[0] += 1

        cb('csp_explore', {
            'node': cur_node,
            'exp': exp_count[0],
            'frn': depth_limit - cur_node['g'],
            'algo': 'Forward Checking',
            'depth': cur_node['g']
        })
        time.sleep(0.04)

        if cur_state == goal:
            return cur_node

        if cur_node['g'] >= depth_limit:
            return None

        for action in get_actions(cur_state):
            next_state = do_move(cur_state, action)
            next_tuple = state_to_tuple(next_state)
            if next_tuple not in visited:
                if not forward_check_fn(next_state):
                    continue
                visited.add(next_tuple)
                child_node = {
                    'state': next_state,
                    'parent': cur_node,
                    'action': action,
                    'g': cur_node['g'] + 1
                }
                res = backtrack(child_node, depth_limit)
                if res is not None:
                    return res
                visited.remove(next_tuple)
        return None

    sol_node = backtrack(root, depth_limit=20)
    if sol_node:
        path_list = trace_path_dict(sol_node)
        cb('done', {'path': path_list, 'exp': exp_count[0], 'frn': 0, 'steps': len(path_list)-1})
    else:
        cb('fail', {'exp': exp_count[0]})


def ac3_search(start, goal, hfn, cb):
    visited = {state_to_tuple(start)}
    root = {'state': start, 'parent': None, 'action': None, 'g': 0}
    exp_count = [0]

    def revise(Xi, Xj, domains):
        revised = False
        for x in domains[Xi][:]:
            supported = False
            next_states_from_x = [do_move(x, a) for a in get_actions(x)]
            for y in domains[Xj]:
                if any(state_to_tuple(y) == state_to_tuple(ns) for ns in next_states_from_x):
                    supported = True
                    break
            if not supported:
                domains[Xi].remove(x)
                revised = True
        return revised

    def AC3(domains):
        queue = [("X_t+1", "X_t+2")]
        while queue:
            Xi, Xj = queue.pop(0)
            if revise(Xi, Xj, domains):
                if len(domains[Xi]) == 0:
                    return False
        return True

    def backtrack(cur_node, depth_limit):
        if not cb('alive', {}):
            return None

        cur_state = cur_node['state']
        exp_count[0] += 1

        cb('csp_explore', {
            'node': cur_node,
            'exp': exp_count[0],
            'frn': depth_limit - cur_node['g'],
            'algo': 'AC-3',
            'depth': cur_node['g']
        })
        time.sleep(0.04)

        if cur_state == goal:
            return cur_node

        if cur_node['g'] >= depth_limit:
            return None

        for action in get_actions(cur_state):
            next_state = do_move(cur_state, action)
            next_tuple = state_to_tuple(next_state)
            if next_tuple not in visited:
                if next_state != goal:
                    domain_t1 = [next_state]
                    domain_t2 = []
                    for act2 in get_actions(next_state):
                        s2 = do_move(next_state, act2)
                        s2_tuple = state_to_tuple(s2)
                        if s2_tuple not in visited and s2_tuple != state_to_tuple(cur_state):
                            domain_t2.append(s2)
                    domains = {
                        "X_t+1": domain_t1,
                        "X_t+2": domain_t2
                    }
                    if not AC3(domains):
                        continue

                visited.add(next_tuple)
                child_node = {
                    'state': next_state,
                    'parent': cur_node,
                    'action': action,
                    'g': cur_node['g'] + 1
                }
                res = backtrack(child_node, depth_limit)
                if res is not None:
                    return res
                visited.remove(next_tuple)
        return None

    sol_node = backtrack(root, depth_limit=20)
    if sol_node:
        path_list = trace_path_dict(sol_node)
        cb('done', {'path': path_list, 'exp': exp_count[0], 'frn': 0, 'steps': len(path_list)-1})
    else:
        cb('fail', {'exp': exp_count[0]})


def min_conflicts_search(start, goal, hfn, cb):
    T = find_min_distance(start, goal)
    if T <= 0:
        cb('done', {'path': [{'state': start, 'action': None}], 'exp': 0, 'frn': 0, 'steps': 0})
        return

    path = [copy.deepcopy(start)] + [copy.deepcopy(start) for _ in range(T - 1)] + [copy.deepcopy(goal)]

    def is_neighbor(s1, s2):
        s1_tuple = state_to_tuple(s1)
        s2_tuple = state_to_tuple(s2)
        for act in get_actions(s1):
            ns = do_move(s1, act)
            if state_to_tuple(ns) == s2_tuple:
                return True
        return False

    def count_local_conflicts(var_idx, val, current_path):
        conflicts = 0
        if not is_neighbor(current_path[var_idx - 1], val):
            conflicts += 1
        if not is_neighbor(val, current_path[var_idx + 1]):
            conflicts += 1
        return conflicts

    def get_total_conflicts(current_path):
        total = 0
        for i in range(len(current_path) - 1):
            if not is_neighbor(current_path[i], current_path[i + 1]):
                total += 1
        return total

    max_steps = 100
    for step in range(max_steps):
        if not cb('alive', {}):
            return

        total_c = get_total_conflicts(path)

        cb('minconflicts_step', {
            'step': step,
            'total_conflicts': total_c,
            'path': path
        })
        time.sleep(0.15)

        if total_c == 0:
            final_path = [{'state': path[0], 'action': None}]
            for i in range(T):
                s_curr = path[i]
                s_next = path[i+1]
                found_act = '?'
                for act in get_actions(s_curr):
                    ns = do_move(s_curr, act)
                    if state_to_tuple(ns) == state_to_tuple(s_next):
                        found_act = act
                        break
                final_path.append({'state': s_next, 'action': found_act})
            cb('done', {'path': final_path, 'exp': step, 'frn': 0, 'steps': T})
            return

        conflicted_vars = []
        for t in range(1, T):
            if count_local_conflicts(t, path[t], path) > 0:
                conflicted_vars.append(t)

        if not conflicted_vars:
            break

        var_to_repair = random.choice(conflicted_vars)
        candidates_set = {state_to_tuple(path[var_to_repair])}

        pred = path[var_to_repair - 1]
        for act in get_actions(pred):
            candidates_set.add(state_to_tuple(do_move(pred, act)))

        succ = path[var_to_repair + 1]
        for act in get_actions(succ):
            candidates_set.add(state_to_tuple(do_move(succ, act)))

        min_conflict = 999
        best_candidates = []
        for cand_tuple in candidates_set:
            cand = [list(row) for row in cand_tuple]
            c_count = count_local_conflicts(var_to_repair, cand, path)
            if c_count < min_conflict:
                min_conflict = c_count
                best_candidates = [cand]
            elif c_count == min_conflict:
                best_candidates.append(cand)

        path[var_to_repair] = random.choice(best_candidates)

    cb('fail', {'exp': max_steps})


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

# Right panel — Uninformed Search (amber / deep-orange)
UNF_BG    = '#FFF8E1';  UNF_BDR   = '#E65100';  UNF_LOG   = '#FFFDE7'

# Right panel — Informed Search (indigo)
INF_BG    = '#F0EEFF';  INF_BDR   = '#5C35C8';  INF_LOG   = '#FAF8FF'

# Right panel — Local Search (emerald)
LOC_BG    = '#EEFFF5';  LOC_BDR   = '#1B8A55';  LOC_LOG   = '#F5FFF9'

# Right panel — CSP Search (purple)
CSP_BG    = '#F3E5F5';  CSP_BDR   = '#7B1FA2';  CSP_LOG   = '#FDF8FF'

# Text
TXT_W    = '#FFFFFF';   TXT_DARK  = '#1A2440'
TXT_MID  = '#4A6080';   TXT_DIM   = '#90A4B8'

# Value colors
CLR_H     = '#C62828';  CLR_G     = '#6A1B9A';  CLR_F     = '#E65100'
CLR_LIMIT = '#1565C0';  CLR_ALGO  = '#2E7D32'
CLR_STEPS = '#7B1FA2';  CLR_H_CUR = '#C62828';  CLR_H_NBR = '#E65100'
CLR_OK    = '#2E7D32';  CLR_FAIL  = '#C62828';  CLR_WARN  = '#E65100'
CLR_EXP   = '#00897B';  CLR_FRN   = '#F57F17'

BTN_SOLVE = '#1565C0';  BTN_RESET = '#B71C1C'

# ═══════════════════════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════════════════════
HEURISTICS = {
    'Misplaced Tiles':    h_misplaced,
    'Manhattan Distance': h_manhattan,
}

# CB2 — Thuat toan (khong chua heuristic nua)
SEARCH_TYPES = {
    'Uninformed Search': [
        'BFS',
        'DFS',
        'IDS',
        'UCS',
    ],
    'Informed Search': [
        'Greedy',
        'A*',
        'IDA*',
    ],
    'Local Search': [
        'Simple HC',
        'Steepest Ascent HC',
        'Stochastic HC',
        'Random Restart HC',
        'Local Beam Search',
        'Simulated Annealing',
    ],
    'CSP Search': [
        'Backtracking Search',
        'Forward Checking',
        'AC-3',
        'Min-conflicts',
    ],
}

# Map algo name -> fn_key
ALGO_FN_KEY = {
    # Uninformed
    'BFS':                'bfs',
    'DFS':                'dfs',
    'IDS':                'ids',
    'UCS':                'ucs',
    # Informed
    'Greedy':             'greedy',
    'A*':                 'astar',
    'IDA*':               'idastar',
    # Local
    'Simple HC':          'simplehc',
    'Steepest Ascent HC': 'steepesthc',
    'Stochastic HC':      'stochastichc',
    'Random Restart HC':  'rrhc',
    'Local Beam Search':  'beamsearch',
    'Simulated Annealing':'sa',
    # CSP
    'Backtracking Search': 'backtracking',
    'Forward Checking':    'forwardchecking',
    'AC-3':                'ac3',
    'Min-conflicts':       'minconflicts',
}

ALGO_FN = {
    'bfs':          bfs_search,
    'dfs':          dfs_search,
    'ids':          ids_search,
    'ucs':          ucs_search,
    'greedy':       greedy_search,
    'astar':        astar_search,
    'idastar':      idastar_search,
    'simplehc':     simple_hc_search,
    'steepesthc':   steepest_ascent_hc_search,
    'stochastichc': stochastic_hc_search,
    'rrhc':         random_restart_hc_search,
    'beamsearch':   local_beam_search_fn,
    'sa':           simulated_annealing_search,
    'backtracking': backtracking_search,
    'forwardchecking': forward_checking_search,
    'ac3':          ac3_search,
    'minconflicts': min_conflicts_search,
}

# Nhom thuat toan theo loai
UNINFORMED_KEYS = {'bfs', 'dfs', 'ids', 'ucs'}
INFORMED_KEYS   = {'greedy', 'astar', 'idastar'}
LOCAL_KEYS      = {'simplehc', 'steepesthc', 'stochastichc', 'rrhc', 'beamsearch', 'sa'}
CSP_KEYS        = {'backtracking', 'forwardchecking', 'ac3', 'minconflicts'}

# Pseudocode cho tung thuat toan local search
DEFAULT_START = [[1,2,3],
              [4,0,6],
              [7,5,8]]
DEFAULT_GOAL  = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]

class CspPanel(tk.Frame):
    def __init__(self, parent, F):
        super().__init__(parent, bg=CSP_BG,
                         highlightbackground=CSP_BDR, highlightthickness=2)
        self._F = F
        self._build()

    def _build(self):
        tk.Frame(self, bg=CSP_BDR, height=3).pack(fill=tk.X)
        inn = tk.Frame(self, bg=CSP_BG)
        inn.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

        tk.Label(inn, text='CSP Search — Thong Tin',
                 bg=CSP_BG, fg=CSP_BDR, font=self._F['hdr']).pack(anchor='w')

        self._cv = {}
        rows = [
            ('Thuat toan', '',                  CLR_ALGO),
            ('Do sau / Buoc', 'do sau hien tai', '#E65100'),
            ('Nodes duyet', 'so node da xet',    CLR_EXP),
            ('Trang thai / Xung dot', 'frontier / conflicts', CLR_FRN),
            ('Steps',       'so buoc ket qua', CLR_STEPS),
        ]
        for key, desc, clr in rows:
            rf = tk.Frame(inn, bg=CSP_BG); rf.pack(fill=tk.X, pady=2)
            tk.Label(rf, text=f'{key}:', bg=CSP_BG, fg=TXT_MID,
                     font=self._F['stat'], width=18, anchor='w').pack(side=tk.LEFT)
            tk.Label(rf, text=desc, bg=CSP_BG, fg=TXT_DIM,
                     font=self._F['stat']).pack(side=tk.LEFT)
            v = tk.Label(rf, text='—', bg=CSP_BG, fg=clr, font=self._F['bdge'])
            v.pack(side=tk.RIGHT)
            self._cv[key] = v

        self._status = tk.Label(inn, text='San sang', bg=CSP_BG,
                                fg=CLR_OK, font=self._F['hdr'])
        self._status.pack(anchor='w', pady=(6, 0))

        tk.Frame(inn, bg=CSP_BDR, height=1).pack(fill=tk.X, pady=(10, 4))
        tk.Label(inn, text='Nhat Ky CSP', bg=CSP_BG, fg=CSP_BDR,
                 font=self._F['hdr']).pack(anchor='w', pady=(0, 4))

        lf = tk.Frame(inn, bg=CSP_BG); lf.pack(fill=tk.BOTH, expand=True)
        self._log = tk.Text(lf, bg=CSP_LOG, fg=TXT_DARK, font=self._F['mono'],
                            relief='flat', wrap=tk.NONE, state=tk.DISABLED,
                            highlightthickness=1, highlightbackground=CSP_BDR)
        vsb = tk.Scrollbar(lf, orient=tk.VERTICAL, command=self._log.yview)
        hsb = tk.Scrollbar(lf, orient=tk.HORIZONTAL, command=self._log.xview)
        self._log.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self._log.pack(fill=tk.BOTH, expand=True)
        self._log.tag_config('explore', foreground='#7B1FA2')
        self._log.tag_config('done',    foreground='#2E7D32')
        self._log.tag_config('fail',    foreground='#C62828')
        self._log.tag_config('info',    foreground='#E65100')

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

    def update_info(self, algo, depth_or_cost, exp, frn, steps):
        self._cv['Thuat toan'].config(text=algo)
        self._cv['Do sau / Buoc'].config(text=str(depth_or_cost))
        self._cv['Nodes duyet'].config(text=str(exp))
        self._cv['Trang thai / Xung dot'].config(text=str(frn))
        self._cv['Steps'].config(text=str(steps))

    def reset(self, fn_key='backtracking'):
        for k in self._cv: self._cv[k].config(text='—')
        self._status.config(text='San sang', fg=CLR_OK)
        self.log_clear()


class UniformedPanel(tk.Frame):
    def __init__(self, parent, F):
        super().__init__(parent, bg=UNF_BG,
                         highlightbackground=UNF_BDR, highlightthickness=2)
        self._F = F
        self._build()

    def _build(self):
        tk.Frame(self, bg=UNF_BDR, height=3).pack(fill=tk.X)
        inn = tk.Frame(self, bg=UNF_BG)
        inn.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

        tk.Label(inn, text='Uninformed Search — Thong Tin',
                 bg=UNF_BG, fg=UNF_BDR, font=self._F['hdr']).pack(anchor='w')

        self._cv = {}
        rows = [
            ('Thuat toan', '',                  CLR_ALGO),
            ('Depth / Cost', 'do sau / chi phi', '#E65100'),
            ('Explored',    'da duyet',          CLR_EXP),
            ('Frontier',    'hang doi hien tai', CLR_FRN),
            ('Steps',       'buoc trong duong di', CLR_STEPS),
        ]
        for key, desc, clr in rows:
            rf = tk.Frame(inn, bg=UNF_BG); rf.pack(fill=tk.X, pady=2)
            tk.Label(rf, text=f'{key}:', bg=UNF_BG, fg=TXT_MID,
                     font=self._F['stat'], width=14, anchor='w').pack(side=tk.LEFT)
            tk.Label(rf, text=desc, bg=UNF_BG, fg=TXT_DIM,
                     font=self._F['stat']).pack(side=tk.LEFT)
            v = tk.Label(rf, text='—', bg=UNF_BG, fg=clr, font=self._F['bdge'])
            v.pack(side=tk.RIGHT)
            self._cv[key] = v

        self._status = tk.Label(inn, text='San sang', bg=UNF_BG,
                                fg=CLR_OK, font=self._F['hdr'])
        self._status.pack(anchor='w', pady=(6, 0))

        tk.Frame(inn, bg=UNF_BDR, height=1).pack(fill=tk.X, pady=(10, 4))
        tk.Label(inn, text='Nhat Ky Kham Pha', bg=UNF_BG, fg=UNF_BDR,
                 font=self._F['hdr']).pack(anchor='w', pady=(0, 4))

        lf = tk.Frame(inn, bg=UNF_BG); lf.pack(fill=tk.BOTH, expand=True)
        self._log = tk.Text(lf, bg=UNF_LOG, fg=TXT_DARK, font=self._F['mono'],
                            relief='flat', wrap=tk.NONE, state=tk.DISABLED,
                            highlightthickness=1, highlightbackground=UNF_BDR)
        vsb = tk.Scrollbar(lf, orient=tk.VERTICAL, command=self._log.yview)
        hsb = tk.Scrollbar(lf, orient=tk.HORIZONTAL, command=self._log.xview)
        self._log.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self._log.pack(fill=tk.BOTH, expand=True)
        self._log.tag_config('explore', foreground='#BF360C')
        self._log.tag_config('done',    foreground='#2E7D32')
        self._log.tag_config('fail',    foreground='#C62828')
        self._log.tag_config('info',    foreground='#E65100')
        self._log.tag_config('depth',   foreground='#6A1B9A')

    _PSEUDOCODES = {}

    # -- Public API --
    def set_status(self, text, clr=None):
        self._status.config(text=text, fg=clr or CLR_OK)

    def set_pseudocode(self, fn_key):   # kept for compat, no-op
        pass

    def log_write(self, msg, tag=''):
        self._log.config(state=tk.NORMAL)
        self._log.insert(tk.END, msg + '\n', tag)
        self._log.see(tk.END)
        self._log.config(state=tk.DISABLED)

    def log_clear(self):
        self._log.config(state=tk.NORMAL)
        self._log.delete('1.0', tk.END)
        self._log.config(state=tk.DISABLED)

    def update_info(self, algo, depth_or_cost, exp, frn, steps):
        self._cv['Thuat toan'].config(text=algo)
        self._cv['Depth / Cost'].config(text=str(depth_or_cost))
        self._cv['Explored'].config(text=str(exp))
        self._cv['Frontier'].config(text=str(frn))
        self._cv['Steps'].config(text=str(steps))

    def reset(self, fn_key='bfs'):
        for k in self._cv: self._cv[k].config(text='—')
        self._status.config(text='San sang', fg=CLR_OK)
        self.log_clear()


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
            ('Thuat toan',      '',                        CLR_ALGO),
            ('Heuristic',       '',                        '#1565C0'),
            ('h(n) hien tai',   'gia tri h hien tai',      CLR_H_CUR),
            ('h(n) lan truoc',  'h o buoc truoc',          CLR_H_NBR),
            ('h(n) min nbr',    'h nho nhat neighbor',     CLR_H_NBR),
            ('So buoc',         'Buoc thuc te',             CLR_STEPS),
            ('Restart / Iter',  'So lan khoi dong lai / vong lap', '#00897B'),
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
        self._log.tag_config('step',    foreground='#1565C0')
        self._log.tag_config('done',    foreground='#2E7D32')
        self._log.tag_config('stuck',   foreground='#C62828')
        self._log.tag_config('info',    foreground='#6A1B9A')
        self._log.tag_config('restart', foreground='#E65100')
        self._log.tag_config('beam',    foreground='#00897B')
        self._log.tag_config('sa',      foreground='#7B1FA2')

    # -- Public API --
    def set_status(self, text, clr=None):
        self._status.config(text=text, fg=clr or CLR_OK)

    def set_pseudocode(self, fn_key):   # kept for compat, no-op
        pass

    def log_write(self, msg, tag=''):
        self._log.config(state=tk.NORMAL)
        self._log.insert(tk.END, msg + '\n', tag)
        self._log.see(tk.END)
        self._log.config(state=tk.DISABLED)

    def log_clear(self):
        self._log.config(state=tk.NORMAL)
        self._log.delete('1.0', tk.END)
        self._log.config(state=tk.DISABLED)

    def update_info(self, h_cur, h_prev, h_nbr_min, steps, heur_name,
                    algo_name='—', extra='—'):
        self._cv['h(n) hien tai'].config(text=str(h_cur))
        self._cv['h(n) lan truoc'].config(text=str(h_prev) if h_prev is not None else '—')
        self._cv['h(n) min nbr'].config(text=str(h_nbr_min) if h_nbr_min is not None else '—')
        self._cv['So buoc'].config(text=str(steps))
        self._cv['Heuristic'].config(text=heur_name)
        self._cv['Thuat toan'].config(text=algo_name)
        self._cv['Restart / Iter'].config(text=str(extra))

    def reset(self):
        for k in self._cv: self._cv[k].config(text='—')
        self._status.config(text='San sang', fg=CLR_OK)
        self.log_clear()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('8-Puzzle Solver — Informed & Local Search')
        self.configure(bg=ROOT_BG)
        self.resizable(True, True)
        self.minsize(1080, 620)

        self._start   = copy.deepcopy(DEFAULT_START)
        self._goal    = copy.deepcopy(DEFAULT_GOAL)
        self._cur     = copy.deepcopy(DEFAULT_START)
        self._running = False
        self._prev_h  = None          # for step tracking
        self._restart_cnt = 0         # for RRHC / Beam counters

        self._type_var  = tk.StringVar(value='Informed Search')
        self._algo_var  = tk.StringVar()
        self._heur_var  = tk.StringVar(value='Misplaced Tiles')  # CB3
        self._beam_k    = tk.IntVar(value=3)                      # Beam width

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
        self._unf_panel = UniformedPanel(self._rc, self._F)
        self._csp_panel = CspPanel(self._rc, self._F)

        self._inf_panel.grid(row=0, column=0, sticky='nsew')
        self._loc_panel.grid(row=0, column=0, sticky='nsew')
        self._unf_panel.grid(row=0, column=0, sticky='nsew')
        self._csp_panel.grid(row=0, column=0, sticky='nsew')
        self._loc_panel.grid_remove()   # hidden by default
        self._unf_panel.grid_remove()   # hidden by default
        self._csp_panel.grid_remove()   # hidden by default
        self._active_panel = self._inf_panel

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
                                  state='readonly', font=self.F_BODY, width=18)
        self._cb2.pack(side=tk.LEFT, pady=10)
        self._cb2.bind('<<ComboboxSelected>>', lambda e: self._on_algo_change())

        self._vsep(hdr)

        # ComboBox 3 — Heuristic (an di khi Uninformed Search)
        self._cb3_lbl = tk.Label(hdr, text='Heuristic:', bg=HDR_BG, fg='#7DD4FC',
                                  font=self.F_BODY)
        self._cb3_lbl.pack(side=tk.LEFT, padx=(4, 2))
        self._cb3 = ttk.Combobox(hdr, textvariable=self._heur_var,
                                  values=list(HEURISTICS.keys()),
                                  state='readonly', font=self.F_BODY, width=17)
        self._cb3.pack(side=tk.LEFT, pady=10)
        self._cb3.bind('<<ComboboxSelected>>', lambda e: self._on_heur_change())
        self._cb3_sep = tk.Frame(hdr, bg=HDR_LINE, width=1, height=30)
        self._cb3_sep.pack(side=tk.LEFT, padx=8, pady=10)

        self._btn_solve = self._btn(hdr, 'Giai',  BTN_SOLVE, self._solve)
        self._btn_solve.pack(side=tk.LEFT, padx=4)
        self._btn(hdr, 'Reset', BTN_RESET, self._reset).pack(side=tk.LEFT, padx=3)

        # Stats (right side) — shared Steps + type-specific
        sf = tk.Frame(hdr, bg=HDR_BG)
        sf.pack(side=tk.RIGHT, padx=10)
        self._lbl_stp = self._badge(sf, 'Steps', '—', CLR_STEPS)

        # Informed/Uniformed shared stats frame (Explored + Frontier)
        self._inf_sf = tk.Frame(sf, bg=HDR_BG)
        self._inf_sf.pack(side=tk.RIGHT)
        self._lbl_exp = self._badge(self._inf_sf, 'Explored', '0', CLR_EXP)
        self._lbl_frn = self._badge(self._inf_sf, 'Frontier', '0', CLR_FRN)

        # Local-only stats frame (hidden by default)
        self._loc_sf = tk.Frame(sf, bg=HDR_BG)
        self._lbl_h   = self._badge(self._loc_sf, 'h(n)', '—', CLR_H_CUR)
        self._lbl_rst = self._badge(self._loc_sf, 'Restart', '—', CLR_WARN)

    #  LEFT — SKY BLUE (boards)
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

    #  LEFT — MINT (animated board + path)
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

    #  WIDGET HELPERS
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

    #  BOARD HELPERS
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

    #  COMBOBOX CHANGE HANDLERS
    def _on_type_change(self):
        stype = self._type_var.get()
        algos = SEARCH_TYPES[stype]
        self._cb2.config(values=algos)
        self._algo_var.set(algos[0])
        self._swap_panel(stype)
        self._update_stats_visibility(stype)
        # An / hien CB3 Heuristic
        if stype == 'Uninformed Search' or stype == 'CSP Search':
            self._cb3_lbl.pack_forget()
            self._cb3.pack_forget()
            self._cb3_sep.pack_forget()
        else:
            self._cb3_lbl.pack(side=tk.LEFT, padx=(4, 2))
            self._cb3.pack(side=tk.LEFT, pady=10)
            self._cb3_sep.pack(side=tk.LEFT, padx=8, pady=10)
        self._on_algo_change()

    def _on_algo_change(self):
        algo_name = self._algo_var.get()
        if not algo_name: return
        fn_key = ALGO_FN_KEY.get(algo_name, 'greedy')
        heur_key = 'manhattan' if self._heur_var.get() == 'Manhattan Distance' else 'misplaced'
        stype = self._type_var.get()
        # --- UX: soft-reset log/path/stats, giu nguyen start state ---
        self._soft_reset(fn_key, heur_key, algo_name, stype)

    def _on_heur_change(self):
        """CB3 change: soft-reset roi cap nhat panel, giu nguyen start state."""
        algo_name = self._algo_var.get()
        fn_key    = ALGO_FN_KEY.get(algo_name, 'greedy')
        heur_key  = 'manhattan' if self._heur_var.get() == 'Manhattan Distance' else 'misplaced'
        stype     = self._type_var.get()
        self._soft_reset(fn_key, heur_key, algo_name, stype)

    def _soft_reset(self, fn_key, heur_key, algo_name, stype):
        """
        Xoa log / duong di / stats / trang thai hien tai ve start,
        NHUNG giu nguyen start-state entries de user click Giai luon.
        Neu dang chay thi dung thread cu truoc.
        """
        # Dung thread dang chay (neu co)
        self._running = False

        # Reset board hien tai ve start (khong thay doi o nhap)
        self._cur    = copy.deepcopy(self._start)
        self._prev_h = None
        self._restart_cnt = 0
        self._update_cur_board(self._cur)

        # Xoa duong di
        self._clear_path()
        tk.Label(self._pi, text='Chua co duong di...',
                 bg=MNT_BG, fg=TXT_DIM, font=self.F_BODY).pack(padx=20, pady=16)

        # Reset badges
        self._lbl_stp.config(text='—')
        self._lbl_frn.config(text='0')
        self._lbl_exp.config(text='0')
        self._lbl_h.config(text='—')
        self._lbl_rst.config(text='—')

        # Reset right panel theo loai
        if stype == 'Uninformed Search':
            self._unf_panel.reset(fn_key)
        elif stype == 'Informed Search':
            self._inf_panel.reset(fn_key, heur_key)
        elif stype == 'CSP Search':
            self._csp_panel.reset(fn_key)
        else:
            self._loc_panel.reset()
            self._loc_panel._cv['Heuristic'].config(text=self._heur_var.get())
            self._loc_panel._cv['Thuat toan'].config(text=algo_name)
            self._loc_panel.set_pseudocode(fn_key)

    def _swap_panel(self, stype):
        # An tat ca panels truoc
        self._unf_panel.grid_remove()
        self._inf_panel.grid_remove()
        self._loc_panel.grid_remove()
        self._csp_panel.grid_remove()
        if stype == 'Uninformed Search':
            self._unf_panel.grid()
            self._active_panel = self._unf_panel
        elif stype == 'Informed Search':
            self._inf_panel.grid()
            self._active_panel = self._inf_panel
        elif stype == 'CSP Search':
            self._csp_panel.grid()
            self._active_panel = self._csp_panel
        else:
            self._loc_panel.grid()
            self._active_panel = self._loc_panel

    def _update_stats_visibility(self, stype):
        if stype == 'Local Search':
            self._inf_sf.pack_forget()
            self._loc_sf.pack(side=tk.RIGHT)
        else:  # Uninformed Search + Informed Search deu can Explored/Frontier
            self._loc_sf.pack_forget()
            self._inf_sf.pack(side=tk.RIGHT)

    #  USER ACTIONS
    def _randomize(self):
        self._start = random_start_state()
        self._cur   = copy.deepcopy(self._start)
        self._refresh_start_entries()
        self._update_cur_board(self._cur)

    def _reset(self):
        self._running = False
        self._start   = random_start_state()
        self._goal    = copy.deepcopy(DEFAULT_GOAL)
        self._cur     = copy.deepcopy(self._start)
        self._prev_h  = None
        self._restart_cnt = 0
        self._refresh_start_entries()
        self._update_cur_board(self._cur)
        self._clear_path()
        tk.Label(self._pi, text='Chua co duong di...',
                 bg=MNT_BG, fg=TXT_DIM, font=self.F_BODY).pack(padx=20, pady=16)
        self._lbl_stp.config(text='—')
        self._lbl_frn.config(text='0')
        self._lbl_exp.config(text='0')
        self._lbl_h.config(text='—')
        self._lbl_rst.config(text='—')
        self._active_panel.set_status('San sang', CLR_OK)
        self._active_panel.log_clear()
        fn_key   = ALGO_FN_KEY.get(self._algo_var.get(), 'greedy')
        heur_key = 'manhattan' if self._heur_var.get() == 'Manhattan Distance' else 'misplaced'
        stype    = self._type_var.get()
        if stype == 'Uninformed Search':
            self._unf_panel.reset(fn_key)
        elif isinstance(self._active_panel, InformedPanel):
            self._active_panel.reset(fn_key, heur_key)
        elif isinstance(self._active_panel, CspPanel):
            self._csp_panel.reset(fn_key)
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
        self._restart_cnt = 0
        self._update_cur_board(self._cur)

        if not is_solvable(self._start, self._goal):
            messagebox.showwarning('Khong giai duoc',
                                   'Trang thai khong the giai!\nHay thu Ngau Nhien.')
            return

        algo_name = self._algo_var.get()
        fn_key    = ALGO_FN_KEY.get(algo_name, 'greedy')
        heur_name = self._heur_var.get()
        hfn       = HEURISTICS[heur_name]
        fn        = ALGO_FN[fn_key]

        self._running = True
        self._clear_path()
        self._lbl_stp.config(text='0')
        self._active_panel.log_clear()
        self._active_panel.set_status('Dang chay...', CLR_WARN)

        if fn_key in UNINFORMED_KEYS:
            self._active_panel.log_write(
                f'[BAT DAU]  {algo_name}  (khong dung heuristic)', 'info')
            self._lbl_exp.config(text='0')
            self._lbl_frn.config(text='0')
        elif fn_key in CSP_KEYS:
            self._active_panel.log_write(
                f'[BAT DAU]  {algo_name}  (CSP formulation)', 'info')
            self._lbl_exp.config(text='0')
            self._lbl_frn.config(text='0')
        elif isinstance(self._active_panel, InformedPanel):
            self._active_panel.log_write(
                f'[BAT DAU]  {algo_name}  |  Heuristic: {heur_name}', 'info')
            self._inf_panel.update_costs(None, fn_key)
            self._lbl_frn.config(text='0')
            self._lbl_exp.config(text='0')
        else:
            self._active_panel.log_write(
                f'[BAT DAU]  {algo_name}  |  Heuristic: {heur_name}', 'info')

        start = copy.deepcopy(self._start)
        goal  = copy.deepcopy(self._goal)

        # Local Beam Search can bien so k
        if fn_key == 'beamsearch':
            threading.Thread(target=fn,
                             args=(start, goal, hfn, self._cb),
                             kwargs={'k': self._beam_k.get()},
                             daemon=True).start()
        else:
            threading.Thread(target=fn,
                             args=(start, goal, hfn, self._cb),
                             daemon=True).start()

    # ─────────────────────────────────────────
    #  UNIFIED CALLBACK
    # ─────────────────────────────────────────
    def _cb(self, event, data):
        if event == 'alive': return self._running

        # ── Uninformed Search events ──────────────
        if event == 'unf_explore':
            node  = data['node']; exp = data['exp']; frn = data['frn']
            algo  = data.get('algo', '?')
            depth = data.get('depth', data.get('cost', data.get('g', '—')))
            lim   = data.get('limit', None)
            self.after(0, lambda n=node, e=exp, f=frn, a=algo, d=depth, l=lim:
                       self._unf_explore(n, e, f, a, d, l))
            time.sleep(0.02)

        # ── Informed Search events ──────────────
        elif event == 'explore':
            node = data['node']; exp = data['exp']; frn = data['frn']
            lim  = data.get('limit')
            self.after(0, lambda n=node, e=exp, f=frn, l=lim:
                       self._inf_explore(n, e, f, l))
            time.sleep(0.05)

        elif event == 'done':
            path  = data['path']
            exp   = data.get('exp', 0)
            frn   = data.get('frn', 0)
            steps = data.get('steps', len(path) - 1)
            rst   = data.get('restarts', data.get('iterations', None))
            self.after(0, lambda p=path, e=exp, f=frn, s=steps, r=rst:
                       self._on_done(p, e, f, s, r))

        elif event == 'fail':
            exp = data.get('exp', 0)
            self.after(0, lambda e=exp: self._on_fail(e))

        # ── Local Search — generic step ─────
        elif event == 'loc_step':
            node  = data['node']; steps = data['steps']
            nhs   = data['neighbors_h']
            algo  = data.get('algo', '—')
            self.after(0, lambda n=node, s=steps, nh=nhs, a=algo:
                       self._loc_step(n, s, nh, a))

        # ── Simple HC (legacy) ──────────────
        elif event == 'shc_step':
            node = data['node']; steps = data['steps']; nhs = data['neighbors_h']
            self.after(0, lambda n=node, s=steps, nh=nhs:
                       self._loc_step(n, s, nh, 'Simple HC'))

        elif event == 'shc_stuck':
            path = data['path']; node = data['node']
            steps = data['steps']; nhs = data['neighbors_h']
            self.after(0, lambda p=path, n=node, s=steps, nh=nhs:
                       self._on_loc_stuck(p, n, s, nh))

        # ── Random Restart HC ───────────────
        elif event == 'rrhc_restart':
            node = data['node']; restart = data['restart']
            self.after(0, lambda n=node, r=restart:
                       self._rrhc_restart(n, r))

        elif event == 'rrhc_local_stuck':
            node = data['node']; restart = data['restart']
            steps = data['steps']; nhs = data['neighbors_h']
            self.after(0, lambda n=node, r=restart, s=steps, nh=nhs:
                       self._rrhc_local_stuck(n, r, s, nh))

        elif event == 'rrhc_fail':
            rst = data['restarts']
            self.after(0, lambda r=rst: self._rrhc_fail(r))

        # ── Local Beam Search ───────────────
        elif event == 'beam_init':
            nodes = data['nodes']; k = data['k']
            self.after(0, lambda ns=nodes, kk=k: self._beam_init(ns, kk))

        elif event == 'beam_step':
            nodes = data['nodes']; k = data['k']
            it    = data['iteration']; h_vals = data['h_vals']
            self.after(0, lambda ns=nodes, kk=k, i=it, hv=h_vals:
                       self._beam_step(ns, kk, i, hv))

        elif event == 'beam_fail':
            it = data['iteration']
            self.after(0, lambda i=it: self._beam_fail(i))

        # ── Simulated Annealing ────────────────────
        elif event == 'sa_step':
            node  = data['node']; steps = data['steps']
            T     = data['T'];    delta = data['delta']
            acc   = data['accepted']; nbrs_h = data['neighbors_h']
            nbr   = data['neighbor']
            self.after(0, lambda n=node, s=steps, t=T, d=delta, a=acc, nh=nbrs_h, nb=nbr:
                       self._sa_step(n, s, t, d, a, nh, nb))

        elif event == 'sa_frozen':
            path  = data['path']; node = data['node']
            steps = data['steps']; T = data['T']
            self.after(0, lambda p=path, n=node, s=steps, t=T:
                       self._sa_frozen(p, n, s, t))

        # ── CSP Search events ──────────────────────
        elif event == 'csp_explore':
            node  = data['node']; exp = data['exp']; frn = data['frn']
            algo  = data.get('algo', '?')
            depth = data.get('depth', '—')
            self.after(0, lambda n=node, e=exp, f=frn, a=algo, d=depth:
                       self._csp_explore(n, e, f, a, d))
            time.sleep(0.04)

        elif event == 'minconflicts_step':
            step  = data['step']; tc = data['total_conflicts']; path = data['path']
            self.after(0, lambda s=step, t=tc, p=path:
                       self._minconflicts_step(s, t, p))
            time.sleep(0.15)

        return None

    # ── Uninformed handlers ────────────────────
    def _unf_explore(self, node, exp, frn, algo, depth, limit):
        self._update_cur_board(node['state'])
        g = node.get('g', depth)
        row = [v for r in node['state'] for v in r]
        msg = f'[#{exp:>4}]  {algo}  depth/cost={g}  frn={frn}  {row}'
        if limit is not None: msg += f'  limit={limit}'
        self._unf_panel.update_info(algo, g, exp, frn, '—')
        self._lbl_exp.config(text=str(exp))
        self._lbl_frn.config(text=str(frn))
        self._lbl_stp.config(text=str(exp))
        self._unf_panel.log_write(msg, 'explore')

    # ── Informed handlers ────────────────────
    def _inf_explore(self, node, exp, frn, limit):
        self._update_cur_board(node['state'])
        algo_name = self._algo_var.get()
        fn_key = ALGO_FN_KEY.get(algo_name, 'greedy')
        self._inf_panel.update_costs(node, fn_key, limit)
        self._lbl_exp.config(text=str(exp))
        self._lbl_frn.config(text=str(frn))
        self._lbl_stp.config(text=str(exp))
        row = [v for r in node['state'] for v in r]
        msg = f'[#{exp:>4}] {row}  h={node["h"]}'
        if fn_key in ('astar', 'idastar'): msg += f'  g={node["g"]}  f={node["f"]}'
        if fn_key == 'idastar' and limit is not None: msg += f'  lim={limit}'
        self._inf_panel.log_write(msg, 'explore')

    def _on_done(self, path, exp, frn, steps, rst):
        self._running = False
        self._lbl_stp.config(text=str(steps))
        if isinstance(self._active_panel, UniformedPanel):
            self._lbl_exp.config(text=str(exp))
            self._lbl_frn.config(text=str(frn))
            algo = self._algo_var.get()
            self._unf_panel.update_info(algo, '—', exp, frn, steps)
            self._unf_panel.set_status(f'Tim thay!  {steps} buoc', CLR_OK)
            self._unf_panel.log_write(
                f'\n[XONG]  {steps} buoc — {exp} nodes kham pha\n', 'done')
        elif isinstance(self._active_panel, InformedPanel):
            self._lbl_exp.config(text=str(exp))
            self._lbl_frn.config(text=str(frn))
            self._inf_panel.set_status(f'Tim thay!  {steps} buoc', CLR_OK)
            self._inf_panel.log_write(f'\n[XONG]  {steps} buoc — {exp} nodes\n', 'done')
        elif isinstance(self._active_panel, CspPanel):
            self._lbl_exp.config(text=str(exp))
            self._lbl_frn.config(text=str(frn))
            algo = self._algo_var.get()
            self._csp_panel.update_info(algo, '—', exp, frn, steps)
            self._csp_panel.set_status(f'Tim thay!  {steps} buoc', CLR_OK)
            self._csp_panel.log_write(
                f'\n[XONG]  {steps} buoc — {exp} nodes/steps\n', 'done')
        else:
            rst_str = f'{rst}' if rst is not None else '—'
            self._lbl_rst.config(text=rst_str)
            self._loc_panel.set_status(f'Tim thay!  {steps} buoc', CLR_OK)
            extra = f'rst={rst}' if rst is not None else ''
            self._loc_panel.log_write(
                f'\n[XONG]  {steps} buoc  {extra}\n', 'done')
            self._loc_panel._cv['So buoc'].config(text=str(steps))
            if rst is not None:
                self._loc_panel._cv['Restart / Iter'].config(text=str(rst))
        self._show_path(path)
        self._animate(path)

    def _on_fail(self, exp):
        self._running = False
        if isinstance(self._active_panel, UniformedPanel):
            self._lbl_exp.config(text=str(exp))
            self._unf_panel.set_status('Khong tim thay duong di!', CLR_FAIL)
            self._unf_panel.log_write(
                f'\n[THAT BAI]  {exp} nodes, khong co duong di.\n', 'fail')
        elif isinstance(self._active_panel, InformedPanel):
            self._lbl_exp.config(text=str(exp))
            self._inf_panel.set_status('Khong tim thay duong di!', CLR_FAIL)
            self._inf_panel.log_write(
                f'\n[THAT BAI]  {exp} nodes, khong co duong di.\n', 'fail')
        elif isinstance(self._active_panel, CspPanel):
            self._lbl_exp.config(text=str(exp))
            self._csp_panel.set_status('Khong tim thay duong di!', CLR_FAIL)
            self._csp_panel.log_write(
                f'\n[THAT BAI]  {exp} nodes/steps, khong co duong di.\n', 'fail')
        else:
            self._loc_panel.set_status('Khong tim thay duong di!', CLR_FAIL)
            self._loc_panel.log_write('\n[THAT BAI]  Khong co duong di.\n', 'stuck')

    # ── Local Search — generic step handler ─
    def _loc_step(self, node, steps, nbrs_h, algo_name):
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
        heur_name = self._heur_var.get()
        self._loc_panel.update_info(h, self._prev_h, h_nbr_min, steps, heur_name,
                                    algo_name=algo_name,
                                    extra=self._restart_cnt)
        self._lbl_h.config(text=str(h))
        self._lbl_stp.config(text=str(steps))
        act = node.action or 'Start'
        msg = f'[Buoc {steps:>3}]  action={str(act):<2}  h(n)={h}'
        if h_nbr_min is not None: msg += f'  h_nbr_min={h_nbr_min}  delta={h-h_nbr_min:+d}'
        self._loc_panel.log_write(msg, 'step')
        self._prev_h = h

    def _on_loc_stuck(self, path, node, steps, nbrs_h):
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

    # ── Random Restart HC handlers ──────────
    def _rrhc_restart(self, node, restart_idx):
        self._restart_cnt = restart_idx
        self._lbl_rst.config(text=str(restart_idx))
        self._loc_panel._cv['Restart / Iter'].config(text=str(restart_idx))
        h = node.h_cost
        self._lbl_h.config(text=str(h))
        heur_name = self._heur_var.get()
        self._loc_panel.update_info(h, None, None, node.step, heur_name,
                                    algo_name='Random Restart HC',
                                    extra=f'restart #{restart_idx}')
        self._loc_panel.log_write(
            f'\n--- [Khoi dong lai #{restart_idx}] ---  h_start={h}', 'restart')
        self._update_cur_board(node.state)

    def _rrhc_local_stuck(self, node, restart_idx, steps, nbrs_h):
        h = node.h_cost
        nbr_str = str(sorted(nbrs_h)) if nbrs_h else '[]'
        self._loc_panel.log_write(
            f'  [Ket cuc bo]  h={h}  buoc={steps}  nbrs={nbr_str}', 'stuck')

    def _rrhc_fail(self, restarts):
        self._running = False
        self._loc_panel.set_status(f'That bai sau {restarts} lan khoi dong!', CLR_FAIL)
        self._loc_panel.log_write(
            f'\n[THAT BAI]  Sau {restarts} lan khoi dong lai, khong tim duoc dich.\n', 'stuck')

    # ── Local Beam Search handlers ──────────
    def _beam_init(self, nodes, k):
        h0 = nodes[0].h_cost if nodes else '?'
        heur_name = self._heur_var.get()
        self._loc_panel.update_info(h0, None, None, 0, heur_name,
                                    algo_name='Local Beam Search',
                                    extra=f'k={k}, iter=0')
        self._lbl_h.config(text=str(h0))
        self._loc_panel.log_write(
            f'[Khoi dau]  k={k}  h_start={h0}', 'beam')
        if nodes: self._update_cur_board(nodes[0].state)

    def _beam_step(self, nodes, k, iteration, h_vals):
        best = nodes[0]
        h    = best.h_cost
        hi   = None
        prev = self._cur
        for i in range(3):
            for j in range(3):
                if prev[i][j] != best.state[i][j] and best.state[i][j] != 0:
                    hi = (i, j)
        self._cur = best.state
        self._update_cur_board(best.state, hi)
        heur_name = self._heur_var.get()
        self._loc_panel.update_info(h, self._prev_h, min(h_vals), best.step, heur_name,
                                    algo_name='Local Beam Search',
                                    extra=f'k={k}, iter={iteration}')
        self._lbl_h.config(text=str(h))
        self._lbl_stp.config(text=str(best.step))
        self._lbl_rst.config(text=str(iteration))
        self._loc_panel._cv['Restart / Iter'].config(text=str(iteration))
        self._loc_panel.log_write(
            f'[Vong {iteration:>3}]  k={k}  h_vals={h_vals}  best_h={h}', 'beam')
        self._prev_h = h

    def _beam_fail(self, iteration):
        self._running = False
        self._loc_panel.set_status(f'That bai sau {iteration} vong lap!', CLR_FAIL)
        self._loc_panel.log_write(
            f'\n[THAT BAI]  Sau {iteration} vong lap, khong tim duoc dich.\n', 'stuck')

    # ── Simulated Annealing handlers ────────────
    def _sa_step(self, node, steps, T, delta, accepted, nbrs_h, neighbor):
        st = node.state; h = node.h_cost
        hi = None
        if steps > 0:
            prev = self._cur
            for i in range(3):
                for j in range(3):
                    if prev[i][j] != st[i][j] and st[i][j] != 0: hi = (i, j)
        self._cur = st
        self._update_cur_board(st, hi)
        heur_name = self._heur_var.get()
        self._loc_panel.update_info(h, self._prev_h,
                                    min(nbrs_h) if nbrs_h else None,
                                    steps, heur_name,
                                    algo_name='Simulated Annealing',
                                    extra=f'T={T}')
        self._lbl_h.config(text=str(h))
        self._lbl_stp.config(text=str(steps))
        # Log format: buoc | T | delta | accepted/rejected | h
        acc_str = 'CHAP NHAN' if accepted else 'tu choi'
        msg = (f'[Buoc {steps:>3}]  T={T:>7.3f}  delta={delta:+d}'
               f'  {acc_str}  h={h}')
        self._loc_panel.log_write(msg, 'sa')
        self._prev_h = h

    def _sa_frozen(self, path, node, steps, T):
        """SA het nhiet do ma chua tim thay dich."""
        self._running = False
        h = node.h_cost
        self._lbl_stp.config(text=str(steps))
        self._loc_panel.set_status(f'Dong bang!  h={h}  T={T}  ({steps} buoc)', CLR_FAIL)
        self._loc_panel.log_write(
            f'\n[DONG BANG]  Nhiet do = {T}, h(n) = {h}, buoc = {steps}\n'
            f'    Khong dat duoc goal truoc khi het nhiet!\n', 'stuck')
        self._show_path(path, stuck=(h > 0))
        self._animate(path)

    # ── CSP handlers ───────────────────────────
    def _csp_explore(self, node, exp, frn, algo, depth):
        self._update_cur_board(node['state'])
        row = [v for r in node['state'] for v in r]
        msg = f'[#{exp:>4}]  {algo}  depth={depth}  budget={frn}  {row}'
        self._csp_panel.update_info(algo, depth, exp, frn, '—')
        self._lbl_exp.config(text=str(exp))
        self._lbl_frn.config(text=str(frn))
        self._lbl_stp.config(text=str(exp))
        self._csp_panel.log_write(msg, 'explore')

    def _minconflicts_step(self, step, total_conflicts, path):
        mid = len(path) // 2
        self._update_cur_board(path[mid])
        msg = f'[Vong {step:>3}]  Xung dot = {total_conflicts}'
        self._csp_panel.update_info('Min-conflicts', f'Iter {step}', step, total_conflicts, '—')
        self._lbl_exp.config(text=str(step))
        self._lbl_frn.config(text=str(total_conflicts))
        self._lbl_stp.config(text=str(step))
        self._csp_panel.log_write(msg, 'explore')


# ═══════════════════════════════════════════════════════════
if __name__ == '__main__':
    App().mainloop()
