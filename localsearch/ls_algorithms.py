import time
import numpy as np
import math

def load_instance(fname):
    with open(fname) as f:
        lines = [l.strip() for l in f if l.strip() and not l.startswith('#')]
    n, m = map(int, lines[0].split())
    U = set(range(1, n+1))
    subsets = []
    for line in lines[1:]:
        parts = list(map(int, line.split()))
        subsets.append(set(parts[1:]))
    return U, subsets


def run_approx(U, subsets):
    """
    Greedy approximation: pick subset covering max uncovered each step.
    """
    uncovered = set(U)
    solution = []
    while uncovered:
        best_idx = max(range(len(subsets)),
                       key=lambda i: len(subsets[i] & uncovered))
        solution.append(best_idx + 1)
        uncovered -= subsets[best_idx]
    return sorted(solution)


def run_ls1(U, subsets, cutoff, seed=None, max_no_improve=10000):
    """
    Hill-Climbing with 2-out/1-in swap neighborhood.
    """
    np.random.seed(seed)
    start = time.time()

    # Initial deterministic greedy cover
    current = set(run_approx(U, subsets))
    best = current.copy()
    trace = [(0.0, len(best))]
    no_improve = 0
    iters = 0
    trace_freq = 100

    while time.time() - start < cutoff and no_improve < max_no_improve:
        iters += 1
        # 2‑out,1‑in move
        if len(current) < 2:
            break
        outs = np.random.choice(list(current), 2, replace=False)
        cand_minus = current - set(outs)
        ins_candidates = [i+1 for i in range(len(subsets)) if i+1 not in cand_minus]
        ins = np.random.choice(ins_candidates)
        cand = cand_minus | {ins}
        # check coverage
        if set().union(*(subsets[i-1] for i in cand)) == U:
            if len(cand) < len(current):
                current = cand
                no_improve = 0
            else:
                no_improve += 1
        else:
            no_improve += 1

        # update best
        if len(current) < len(best):
            best = current.copy()
            elapsed = time.time() - start
            trace.append((elapsed, len(best)))
            no_improve = 0
        
        # periodic trace update
        if iters % trace_freq == 0:
            elapsed = time.time() - start
            trace.append((elapsed, len(best)))


    return sorted(best), trace


def run_ls2(U, subsets, cutoff, seed=None, max_no_improve=10000):
    """
    Simulated Annealing with penalty for uncovered elements,
    2-out/1-in neighbor, and SA-style acceptance.
    """
    np.random.seed(seed)
    start = time.time()

    def objective(sol):
        covered = set().union(*(subsets[i-1] for i in sol))
        pen = len(U) - len(covered)
        return len(sol) + 10000 * pen

    # initialize from deterministic greedy
    current = set(run_approx(U, subsets))
    best = current.copy()
    trace = [(0.0, len(best))]
    no_improve = 0
    iters = 0
    T = 25.0 
    alpha = 0.99 
    trace_freq = 100

    while time.time() - start < cutoff and no_improve < max_no_improve:
        iters += 1

        # propose 2-out/1-in neighbor
        if len(current) < 2:
            break
        outs = np.random.choice(list(current), size=2, replace=False)
        cand_minus = current - set(outs)

        ins_cand = [i+1 for i in range(len(subsets)) if i+1 not in cand_minus]
        if not ins_cand:
            no_improve += 1
            continue
        ins = np.random.choice(ins_cand)
        cand = cand_minus | {ins}

        # evaluate and accept/reject
        cur_obj = objective(current)
        cand_obj = objective(cand)
        delta = cand_obj - cur_obj
        if delta <= 0 or np.random.random() < math.exp(-delta / max(T, 1e-8)):
            current = cand
            cur_obj = cand_obj
            no_improve = 0
        else:
            no_improve += 1

        # record improvement
        if cur_obj < objective(best):
            best = current.copy()
            elapsed = time.time() - start
            trace.append((elapsed, len(best)))
            no_improve = 0

        # periodic trace
        if iters % trace_freq == 0:
            elapsed = time.time() - start
            trace.append((elapsed, len(best)))

        # cool down
        T *= alpha

    covered = set().union(*(subsets[i-1] for i in best))
    if len(covered) < len(U):
        best = set(run_approx(U, subsets))

    return sorted(best), trace
