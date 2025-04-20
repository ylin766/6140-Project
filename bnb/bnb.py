import time
import sys
import os
import math
from typing import List, Set, Tuple

# ======================== 数据读取 ========================
def read_input_file(filename: str):
    with open(filename, 'r') as f:
        lines = f.readlines()
    n, m = map(int, lines[0].split())
    subsets: List[Set[int]] = []
    for line in lines[1:]:
        parts = list(map(int, line.strip().split()))
        subsets.append(set(parts[1:])) 
    universe = set(range(1, n + 1))
    return universe, subsets

# ======================== 贪心 ========================
def greedy_set_cover(universe: Set[int], subsets: List[Set[int]]) -> List[int]:
    remaining = universe.copy()
    chosen: List[int] = []
    while remaining:
        best_idx = -1
        best_gain = -1
        for idx, s in enumerate(subsets):
            gain = len(s & remaining)
            if gain > best_gain:
                best_idx = idx
                best_gain = gain
        chosen.append(best_idx)
        remaining -= subsets[best_idx]
    return chosen

# ======================== BnB ========================
def branch_and_bound(universe: Set[int],
                     subsets: List[Set[int]],
                     cutoff_time: int):
    start_time = time.time()

    # === 位编码 ===
    elem_to_pos = {e: i for i, e in enumerate(sorted(universe))}
    total_bits = (1 << len(universe)) - 1
    bit_subsets: List[int] = []
    for s in subsets:
        bits = 0
        for e in s:
            bits |= 1 << elem_to_pos[e]
        bit_subsets.append(bits)

    # === 预处理：按覆盖元素数降序 ===
    order = sorted(range(len(subsets)),
                   key=lambda i: (bit_subsets[i].bit_count(), -i),  
                   reverse=True)
    bit_subsets = [bit_subsets[i] for i in order]
    orig_index = {new_i: old_i for new_i, old_i in enumerate(order)}

    # === 上界 ===
    best_solution = sorted(greedy_set_cover(universe, subsets))
    best_size = len(best_solution)
    trace: List[Tuple[float, int]] = [(0.0, best_size)]

    # === 下界估计 ===
    def lower_bound(rem_bits: int, start_idx: int) -> int:
        if rem_bits == 0:
            return 0
        uncovered_cnt = rem_bits.bit_count()
        max_per_set = 0
        for i in range(start_idx, len(bit_subsets)):
            cover_cnt = (bit_subsets[i] & rem_bits).bit_count()
            max_per_set = max(max_per_set, cover_cnt)
            if max_per_set == uncovered_cnt:
                break
        if max_per_set == 0:
            return math.inf
        return math.ceil(uncovered_cnt / max_per_set)

    # === DFS ===
    def dfs(idx: int, rem_bits: int, chosen_new_idx: List[int]):
        nonlocal best_solution, best_size

        if rem_bits == 0:
            candidate = sorted(orig_index[i] for i in chosen_new_idx)  
            if len(candidate) < best_size or (len(candidate) == best_size and candidate < best_solution):
                best_solution = candidate
                best_size = len(candidate)
                trace.append((time.time() - start_time, best_size))
            return

        if time.time() - start_time > cutoff_time:
            return

        # 剪枝
        lb = lower_bound(rem_bits, idx)
        if len(chosen_new_idx) + lb > best_size:
            return

        for i in range(idx, len(bit_subsets)):
            if bit_subsets[i] & rem_bits == 0:
                continue
            dfs(i + 1,
                rem_bits & ~bit_subsets[i],
                chosen_new_idx + [i])

    dfs(0, total_bits, [])

    return best_solution, best_size, trace

# ======================== 输出 ========================

def write_solution_file(filename: str, solution, size: int):
    os.makedirs("output", exist_ok=True)
    with open(os.path.join("output", filename), 'w') as f:
        f.write(f"{size}\n")
        f.write(" ".join(str(i + 1) for i in solution) + "\n")


def write_trace_file(filename: str, trace):
    os.makedirs("output", exist_ok=True)
    with open(os.path.join("outpat", filename), 'w') as f:
        for t, val in trace:
            f.write(f"{t:.2f} {val}\n")

# ======================== main ========================

def main():
    args = sys.argv[1:]
    inst_idx = args.index("-inst") + 1
    alg_idx = args.index("-alg") + 1
    time_idx = args.index("-time") + 1

    filename = args[inst_idx]
    algorithm = args[alg_idx]
    cutoff_time = int(args[time_idx])

    instance_name = os.path.splitext(os.path.basename(filename))[0]
    out_sol = f"{instance_name}_{algorithm}_{cutoff_time}.sol"
    out_trace = f"{instance_name}_{algorithm}_{cutoff_time}.trace"

    universe, subsets = read_input_file(filename)
    solution, size, trace = branch_and_bound(universe, subsets, cutoff_time)

    write_solution_file(out_sol, solution, size)
    write_trace_file(out_trace, trace)


if __name__ == "__main__":
    main()
