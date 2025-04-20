import argparse
import time
import os
import numpy as np
from ls_algorithms import (
    load_instance,
    run_ls1,
    run_ls2,
)

def write_solution(sol_idx, prefix):
    with open(f"{prefix}.sol", 'w') as f:
        f.write(f"{len(sol_idx)}\n")
        f.write(' '.join(map(str, sol_idx)) + '\n')


def write_trace(trace, prefix):
    with open(f"{prefix}.trace", 'w') as f:
        for t, q in trace:
            f.write(f"{t:.4f} {q}\n")


parser = argparse.ArgumentParser(description='Min Set Cover Solver')
parser.add_argument('--inst', required=True,
                    help='Instance base name (e.g., test1, small2, large3)')
parser.add_argument('--alg', required=True,
                    choices=['LS1', 'LS2'],
                    help='Algorithm to run')
parser.add_argument('--time', type=float, required=True, help='Cutoff time (s)')
parser.add_argument('--seeds', nargs='+', type=int, default=list(range(1, 21*10, 10)),
                    help='Random seeds for LS (default: 1-20)')
args = parser.parse_args()

base = args.inst
in_file = os.path.join('../data/', f"{base}.in")
if not os.path.isfile(in_file):
    parser.error(f"Input file not found: {in_file}")

U, subsets = load_instance(in_file)


for seed in args.seeds:
    np.random.seed(seed)
    start = time.time()
    if args.alg == 'LS1':
        sol_idx, trace = run_ls1(U, subsets, args.time, seed)
    else:
        sol_idx, trace = run_ls2(U, subsets, args.time, seed)
    elapsed = time.time() - start

    prefix = f"./output/{base}_{args.alg}_{int(args.time)}_{seed}"
    write_solution(sol_idx, prefix)
    write_trace(trace, prefix)
    print(f"Done: alg={args.alg}, seed={seed}, size={len(sol_idx)}, time={elapsed:.2f}s")
