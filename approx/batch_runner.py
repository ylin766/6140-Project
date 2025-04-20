import subprocess
import re
import os
import sys
from decimal import Decimal, ROUND_HALF_UP

DATA_DIR = "data"
SCRIPT_TO_RUN = "set_cover_approx.py"
ALGORITHM_NAME = "Approx"
CUTOFF_TIME = 600
RANDOM_SEED = 0

small_datasets = [f"small{i}" for i in range(1, 19)]
large_datasets = [f"large{i}" for i in range(1, 13)]
all_datasets = small_datasets + large_datasets

def run_instance(dataset_name):
    instance_file = os.path.join(DATA_DIR, f"{dataset_name}.in")
    print(f"--- Running dataset: {dataset_name} ---")

    if not os.path.exists(instance_file):
        print(f"ERROR: Input file not found: {instance_file}")
        return None

    command = [
        sys.executable,
        SCRIPT_TO_RUN,
        "-inst", instance_file,
        "-alg", ALGORITHM_NAME,
        "-time", str(CUTOFF_TIME),
        "-seed", str(RANDOM_SEED)
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False, timeout=CUTOFF_TIME + 60)

        stdout = result.stdout
        stderr = result.stderr

        if result.returncode != 0:
            print(f"ERROR: Subprocess for {dataset_name} failed with return code {result.returncode}")
            print("STDERR:", stderr)
            return None

        time_match = re.search(r"Greedy algorithm finished in (\d+\.?\d*) seconds", stdout)
        size_match = re.search(r"Algorithm found cover with (\d+) subsets", stdout)
        rel_err_match = re.search(r"Relative Error:.*?=\s*(-?\d+\.?\d*)", stdout)
        if not rel_err_match:
             rel_err_match = re.search(r"Relative Error: Infinite", stdout)

        time_val = float(time_match.group(1)) if time_match else None
        size_val = int(size_match.group(1)) if size_match else None

        rel_err_val = None
        if rel_err_match:
             if "Infinite" in rel_err_match.group(0):
                 rel_err_val = float('inf')
             else:
                 try:
                      rel_err_val = float(rel_err_match.group(1))
                 except (IndexError, ValueError):
                      rel_err_val = None

        valid_match = re.search(r"Solution is VALID", stdout)
        if not valid_match:
             print(f"WARNING: Solution validity check did not pass or wasn't found in output for {dataset_name}.")

        if time_val is None or size_val is None:
             print(f"ERROR: Failed to parse time or size from output for {dataset_name}. Check script output.")
             return {
                 'Dataset': dataset_name,
                 'Algorithm': ALGORITHM_NAME,
                 'Time': time_val,
                 'Size': size_val,
                 'RelErr': rel_err_val
             }

        return {
            'Dataset': dataset_name,
            'Algorithm': ALGORITHM_NAME,
            'Time': time_val,
            'Size': size_val,
            'RelErr': rel_err_val
        }

    except subprocess.TimeoutExpired:
         print(f"ERROR: Subprocess for {dataset_name} timed out after {CUTOFF_TIME + 60} seconds.")
         return None
    except FileNotFoundError:
        print(f"ERROR: Script '{SCRIPT_TO_RUN}' not found. Make sure it's in the correct path.")
        return None
    except Exception as e:
        print(f"ERROR: An unexpected error occurred while running {dataset_name}: {e}")
        return None

def format_results_latex(results):
    if not results:
        return "\\textit{No results to display.}"

    def format_float(value):
        if value is None:
            return "N/A"
        if value == float('inf'):
             return "$\\infty$"
        return str(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    latex_string = "\\begin{tabular}{l l r r r}\n"
    latex_string += "\\hline\n"
    latex_string += "\\textbf{Dataset} & \\textbf{Algorithm} & \\textbf{Time(s)} & \\textbf{Coll. Size} & \\textbf{RelErr} \\\\\n"
    latex_string += "\\hline\n"

    for res in results:
        dataset = res['Dataset'].replace('_', '\\_')
        algo = res['Algorithm']
        time_str = format_float(res.get('Time'))
        size_str = str(res.get('Size', 'N/A'))
        rel_err_str = format_float(res.get('RelErr'))

        latex_string += f"{dataset} & {algo} & {time_str} & {size_str} & {rel_err_str} \\\\\n"

    latex_string += "\\hline\n"
    latex_string += "\\end{tabular}\n"

    return latex_string

if __name__ == "__main__":
    print("Starting batch run...")
    all_results = []
    for dataset in all_datasets:
        result_data = run_instance(dataset)
        if result_data:
            all_results.append(result_data)
        else:
            print(f"Skipping {dataset} due to errors.")
        print("-" * 30)

    print("\nBatch run finished.")
    print("Generating LaTeX table...")

    latex_output = format_results_latex(all_results)

    print("\n--- LaTeX Table Code ---")
    print(latex_output)
    print("--- End LaTeX Table Code ---")

    try:
        with open("results_table.tex", "w") as f:
            f.write(latex_output)
        print("\nLaTeX table code also saved to 'results_table.tex'")
    except IOError as e:
        print(f"\nWarning: Could not save LaTeX table to file: {e}")