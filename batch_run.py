import os
import argparse
import subprocess

def get_target_files(data_dir, prefix, valid_range):
    files = []
    for fname in os.listdir(data_dir):
        if fname.startswith(prefix) and fname.endswith(".in"):
            suffix = fname[len(prefix):-3]
            if suffix.isdigit() and int(suffix) in valid_range:
                files.append(os.path.join(data_dir, fname))
    return sorted(files)

def verify_solution(input_file, sol_file, prefix):
    try:
        out_path = os.path.join("output", sol_file)
        out_file = input_file.replace(".in", ".out")
        if not os.path.exists(out_file):
            print(f"⚠️ 无参考输出文件 {out_file}，跳过比对。")
            return

        with open(out_path, 'r') as f1, open(out_file, 'r') as f2:
            sol_lines = [line.strip() for line in f1.readlines()]
            ref_lines = [line.strip() for line in f2.readlines()]

        if prefix == "test":
            if sol_lines[:2] == ref_lines[:2]:
                print(f"✅ {sol_file} 输出与参考完全一致")
            else:
                print(f"❌ {sol_file} 输出不一致\n    期望: {ref_lines[:2]}\n    实际: {sol_lines[:2]}")
        else:
            if sol_lines[0] == ref_lines[0]:
                print(f"✅ {sol_file} 最优值正确")
            else:
                print(f"❌ {sol_file} 最优值错误\n    期望: {ref_lines[0]}\n    实际: {sol_lines[0]}")
    except Exception as e:
        print(f"⚠️ 比对失败 {sol_file}: {e}")

def batch_run(data_dir, prefix, valid_range, cutoff, script):
    files = get_target_files(data_dir, prefix, valid_range)
    if not files:
        print(f"⚠️ 未找到匹配文件（目录={data_dir}, 前缀={prefix}, 范围={list(valid_range)}）")
        return

    print(f" 共找到 {len(files)} 个输入文件：{files}")
    for filepath in files:
        instance_name = os.path.splitext(os.path.basename(filepath))[0]
        sol_file = f"{instance_name}_BnB_{cutoff}.sol"
        trace_file = f"{instance_name}_BnB_{cutoff}.trace"

        cmd = [
            "python", script,
            "-inst", filepath,
            "-alg", "BnB",
            "-time", str(cutoff),
            "-seed", "0"
        ]
        print(f"\n 正在执行：{' '.join(cmd)}")
        subprocess.run(cmd)

        verify_solution(filepath, sol_file, prefix)

def parse_args():
    parser = argparse.ArgumentParser(description="批量运行 BnB 并验证输出")
    parser.add_argument("--prefix", choices=["test", "small", "large"], required=True, help="文件前缀")
    parser.add_argument("--start", type=int, required=True, help="起始编号")
    parser.add_argument("--end", type=int, required=True, help="结束编号")
    parser.add_argument("--time", type=int, default=600, help="超时（秒）")
    parser.add_argument("--script", type=str, default="bnb.py", help="主程序脚本（默认 bnb.py）")
    parser.add_argument("--data", type=str, default="data", help="数据目录（默认 data/）")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    batch_run(
        data_dir=args.data,
        prefix=args.prefix,
        valid_range=range(args.start, args.end + 1),
        cutoff=args.time,
        script=args.script
    )


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
