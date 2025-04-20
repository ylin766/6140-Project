import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def read_trace(prefix):
    trace = []
    with open(prefix + '.trace') as f:
        for line in f:
            t, q = map(float, line.split())
            trace.append((t, q))
    return trace

def time_to_quality(trace, target):
    for t, q in trace:
        if q <= target:
            return t
    return float('inf')

def quality_at_time(trace, tpt):
    best = float('inf')
    for t, q in trace:
        if t <= tpt and q < best:
            best = q
    return best if best < float('inf') else trace[0][1]

def plot_qrt(inst, alg, opt, seeds, cutoff, q_stars, out_dir):
    solve_times = {}
    for q in q_stars:
        thr = opt * (1 + q)
        qt = []
        for s in seeds:
            fname = f"./output/{inst}_{alg}_{cutoff}_{s}"
            trace = read_trace(fname)
            qt.append(time_to_quality(trace, thr))
        solve_times[q] = np.array(qt)

    max_time = 5
    grid = np.linspace(0, max_time, 200)
    plt.figure()
    for q in q_stars:
        times_q = solve_times[q]
        print(times_q)
        fracs = [(times_q <= t).mean() for t in grid]
        plt.plot(grid, fracs, label=f"q*={100*q:.1f}%")
    plt.xlabel("Time (s)")
    plt.ylabel("Fraction solved")

    if alg == "LS1":
        plt.title(f"QRTD: Hill Climbing on {inst}")
    else:
        plt.title(f"QRTD: Simulated Annealing on {inst}")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"{out_dir}/qrt_{inst}_{alg}.png")
    plt.close()

def plot_sqd(inst, alg, opt, seeds, cutoff, out_dir, num_points=200):
    traces = []
    for s in seeds:
        fname = f"./output/{inst}_{alg}_{cutoff}_{s}"
        traces.append(read_trace(fname))
    max_time = 3

    times = np.linspace(0.1 * max_time, max_time, num_points)
    times = np.around(times, 3)

    medians, q1, q3 = [], [], []
    for t in times:
        rels = []
        for trace in traces:
            q_best = quality_at_time(trace, t)
            rels.append((q_best - opt) / opt)
        rels = np.array(rels)
        medians.append(np.median(rels))
        q1.append(np.percentile(rels, 25))
        q3.append(np.percentile(rels, 75))

    plt.figure()
    plt.fill_between(times, q1, q3, alpha=0.3, label='IQR')
    plt.plot(times, medians, label='Median RelErr')
    plt.xlabel("Time (s)")
    plt.ylabel("Relative error")
    if alg == "LS1":
        plt.title(f"SQD: Hill Climbing on {inst}")
    else:
        plt.title(f"SQD: Simulated Annealing on {inst}")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"{out_dir}/sqd_{inst}_{alg}.png")
    plt.close()

def plot_runtime_variation(inst, algs, opt, cutoff, seeds, out_dir):
    plt.figure()
    data = []
    labels = []

    for alg in algs:
        conv_times = []
        for s in seeds:
            prefix = os.path.join('./output', f"{inst}_{alg}_{cutoff}_{s}")
            trace = read_trace(prefix)
            # find the best (lowest) quality seen
            best_q = min(q for _, q in trace)
            # find the first time that quality was reached
            t_first = next(t for t, q in trace if q == best_q)
            if opt >= best_q:
                conv_times.append(t_first)
            else:
                conv_times.append(trace[-1][0])
        data.append(conv_times)
        if alg == "LS1":
            labels.append("Hill Climbing")
        else:
            labels.append("Simulated Annealing")

    plt.boxplot(data, labels=labels)
    plt.xlabel("Algorithm")
    plt.ylabel("Convergence time (s)")
    plt.title(f"Runtime Variation (time to best solution): {inst}")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, f"runtime_variation_{inst}.png"))
    plt.close()

def build_comprehensive_table(instances, algs, seeds, cutoff, opt_vals, out_dir):
    records = []
    for inst in instances:
        opt = opt_vals.get(inst)
        for alg in algs:
            times = []
            quals = []
            for s in seeds:
                prefix = f"{inst}_{alg}_{cutoff}_{s}"
                sol_path = os.path.join('./output', prefix + '.sol')
                with open(sol_path) as fsol:
                    q = int(fsol.readline().strip())
                quals.append(q)
                trace_path = os.path.join('./output', prefix + '.trace')
                if os.path.exists(trace_path):
                    lt = 0.0
                    with open(trace_path) as ftr:
                        for line in ftr:
                            t, _ = map(float, line.split())
                            lt = t
                    times.append(lt)
                else:
                    times.append(0.0)
            avg_q = np.mean(quals)
            avg_t = np.mean(times)
            relerr = (avg_q - opt) / opt if opt else None
            records.append({
                'Dataset': inst,
                'Algorithm': alg,
                'AvgTime(s)': round(avg_t, 2),
                'AvgCollection Size': round(avg_q, 2),
                'RelErr': round(relerr, 4) if relerr is not None else None
            })
    df = pd.DataFrame(records)
    table_csv = os.path.join(out_dir, 'comprehensive_table.csv')
    df.to_csv(table_csv, index=False)
    print(f"Comprehensive table saved to {table_csv}")
    print(df.pivot(index='Dataset', columns='Algorithm', values=['AvgTime(s)','AvgCollection Size','RelErr']))


parser = argparse.ArgumentParser()
parser.add_argument('--inst', nargs='+', required=True,
                    help='List of instance base names (e.g., small1, large2)')
parser.add_argument('--algs', nargs='+', default=['LS1','LS2'],
                    help='Algorithms to evaluate')
parser.add_argument('--seeds', nargs='+', type=int, default=list(range(1,21*10, 10)),
                    help='Random seeds (default: 1-20)')
parser.add_argument('--time', type=int, required=True,
                    help='Time cutoff used in runs')
parser.add_argument('--out_dir', default='./figures',
                    help='Directory to save plots and table')
args = parser.parse_args()

os.makedirs(args.out_dir, exist_ok=True)
opt_vals = {}
for inst in args.inst:
    out_file = os.path.join('./data/', f"{inst}.out")
    with open(out_file) as f:
        opt_vals[inst] = int(f.readline().strip())


q_stars = [0.01, 0.05, 0.1]

for inst in ["large1", "large10"]:
    for alg in [a for a in args.algs if a.startswith('LS')]:
        plot_qrt(inst, alg, opt_vals[inst], args.seeds, args.time, q_stars, args.out_dir)

        plot_sqd(inst, alg, opt_vals[inst], args.seeds, args.time, args.out_dir)
    plot_runtime_variation(inst, args.algs, opt_vals[inst], args.time, args.seeds, args.out_dir)

build_comprehensive_table(args.inst, args.algs, args.seeds, args.time, opt_vals, args.out_dir)