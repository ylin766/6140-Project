import time
import argparse
import os
import math

def read_instance(filename):
    subsets = []
    try:
        with open(filename, 'r') as f:
            first_line = f.readline().strip().split()
            if len(first_line) != 2:
                raise ValueError("First line must contain n and m.")
            n = int(first_line[0])
            m = int(first_line[1])

            for i in range(m):
                line = f.readline().strip().split()
                if not line:
                     print(f"Warning: Encountered unexpected empty line reading subset {i+1}/{m}.")
                     subsets.append(set())
                     continue
                try:
                    elements = {int(x) for x in line[1:]}
                    subsets.append(elements)
                except (ValueError, IndexError) as e:
                    print(f"Error parsing line for subset {i+1}: '{' '.join(line)}'. Error: {e}")
                    raise ValueError(f"Invalid format in subset line {i+2}.")


            if len(subsets) != m:
                print(f"Warning: Read {len(subsets)} subsets, but header specified {m}.")
                m = len(subsets)

            all_elements_in_subsets = set().union(*subsets)
            expected_universe = set(range(1, n + 1))
            if not expected_universe.issubset(all_elements_in_subsets):
                 uncovered_by_any = expected_universe - all_elements_in_subsets
                 print(f"Warning: Elements {uncovered_by_any} are not present in any subset. Full cover might be impossible.")
            invalid_elements = all_elements_in_subsets - expected_universe
            if invalid_elements:
                 print(f"Warning: Subsets contain elements outside the universe [1, {n}]: {invalid_elements}")

            return n, m, subsets

    except FileNotFoundError:
        print(f"Error: Input file '{filename}' not found.")
        exit(1)
    except ValueError as e:
        print(f"Error reading file '{filename}': {e}")
        exit(1)
    except Exception as e:
        print(f"An unexpected error occurred while reading '{filename}': {e}")
        exit(1)


def read_optimal_value(instance_filename):
    base_name = os.path.splitext(instance_filename)[0]
    opt_filename = base_name + ".out"

    if not os.path.exists(opt_filename):
        opt_filename = base_name + ".sol"
        if not os.path.exists(opt_filename):
             print(f"Warning: Optimal solution file ('{base_name}.out' or '{base_name}.sol') not found. Cannot calculate accuracy.")
             return None

    try:
        with open(opt_filename, 'r') as f:
            line = f.readline().strip()
            optimal_size = int(line)
            return optimal_size
    except (IOError, ValueError, IndexError) as e:
        print(f"Error reading or parsing optimal solution file '{opt_filename}': {e}")
        return None


def verify_cover(universe_size, subsets_in_cover, all_subsets_map):
    expected_universe = set(range(1, universe_size + 1))
    actual_coverage = set()
    for index in subsets_in_cover:
        if index in all_subsets_map:
            actual_coverage.update(all_subsets_map[index])
        else:
            print(f"Error in verification: Index {index} not found in original subsets map.")
            return False

    is_valid = (actual_coverage == expected_universe)
    if not is_valid:
        missing_elements = expected_universe - actual_coverage
        print(f"Verification FAILED: The solution does not cover all elements.")
        print(f"Missing elements: {missing_elements}")
    else:
        print("Verification PASSED: The solution correctly covers the universe.")

    return is_valid


def greedy_set_cover(universe_size, subsets):
    start_time = time.time()

    universe = set(range(1, universe_size + 1))
    uncovered_elements = universe.copy()
    cover_indices = []
    all_subsets_map = {i + 1: s for i, s in enumerate(subsets)}
    indexed_subsets = list(all_subsets_map.items())

    while uncovered_elements:
        best_subset_index = -1
        elements_added_by_best = set()
        max_covered_count = -1

        for idx, current_subset in indexed_subsets:
            newly_covered = current_subset.intersection(uncovered_elements)
            count = len(newly_covered)

            if count > max_covered_count:
                max_covered_count = count
                best_subset_index = idx
                elements_added_by_best = newly_covered

        if best_subset_index == -1 or max_covered_count == 0:
            if not uncovered_elements:
                 break
            else:
                 print("Error: Could not cover all elements. Remaining uncovered:", uncovered_elements)
                 return None, all_subsets_map

        cover_indices.append(best_subset_index)
        uncovered_elements -= elements_added_by_best

    end_time = time.time()
    print(f"Greedy algorithm finished in {end_time - start_time:.4f} seconds.")
    return sorted(cover_indices), all_subsets_map


def write_solution_file(instance_name, method, cutoff, cover_indices):
    sol_filename = f"{instance_name}_{method}_{cutoff}.sol"
    try:
        with open(sol_filename, 'w') as f:
            f.write(f"{len(cover_indices)}\n")
            f.write(" ".join(map(str, cover_indices)) + "\n")
        print(f"Solution file created: {sol_filename}")
    except IOError as e:
        print(f"Error writing solution file '{sol_filename}': {e}")
        exit(1)


def main():
    parser = argparse.ArgumentParser(description="Minimum Set Cover Solver - Approximation Algorithm")
    parser.add_argument("-inst", required=True, help="Instance filename (e.g., data/test1.in)")
    parser.add_argument("-alg", required=True, choices=['Approx'], help="Algorithm to use (only Approx supported)")
    parser.add_argument("-time", required=True, type=int, help="Cutoff time in seconds (used for filename)")
    parser.add_argument("-seed", type=int, default=None, help="Random seed (ignored)")

    args = parser.parse_args()

    if args.alg != 'Approx':
        print(f"Error: This script only implements the 'Approx' algorithm.")
        exit(1)

    print(f"--- Running Set Cover Approximation Algorithm ---")
    print(f"Instance: {args.inst}")
    print(f"Cutoff time: {args.time} seconds")
    if args.seed is not None:
        print(f"Random Seed: {args.seed} (Note: Approximation algorithm is deterministic)")

    n, m, subsets = read_instance(args.inst)
    if n is None:
        exit(1)
    print(f"Universe size (n): {n}, Number of subsets (m): {m}")

    cover_indices, all_subsets_map = greedy_set_cover(n, subsets)

    if cover_indices is not None:
        alg_solution_size = len(cover_indices)
        print(f"Algorithm found cover with {alg_solution_size} subsets.")

        print("\n--- Verifying Solution ---")
        is_valid_cover = verify_cover(n, cover_indices, all_subsets_map)
        if not is_valid_cover:
             print("ERROR: The generated solution is INVALID (does not cover the universe).")
        else:
             print("Solution is VALID.")

        print("\n--- Checking Accuracy ---")
        optimal_size = read_optimal_value(args.inst)

        if optimal_size is not None:
            print(f"Known Optimal Solution Size: {optimal_size}")
            if optimal_size > 0:
                relative_error = (alg_solution_size - optimal_size) / optimal_size
                print(f"Relative Error: ({alg_solution_size} - {optimal_size}) / {optimal_size} = {relative_error:.4f}")
                approx_ratio = alg_solution_size / optimal_size
                print(f"Approximation Ratio: {alg_solution_size} / {optimal_size} = {approx_ratio:.4f}")
            elif alg_solution_size == 0 and optimal_size == 0:
                 print("Relative Error: 0.0000 (Optimal and found solution are both size 0)")
                 print("Approximation Ratio: Not applicable (division by zero)")
            else:
                 print(f"Relative Error: Infinite (Optimal is 0, found {alg_solution_size})")
                 print(f"Approximation Ratio: Infinite")
        else:
            print("Could not determine optimal size. Accuracy metrics cannot be calculated.")

        print("\n--- Writing Output ---")
        instance_base_name = os.path.splitext(os.path.basename(args.inst))[0]
        write_solution_file(instance_base_name, args.alg, args.time, cover_indices)

        if not is_valid_cover:
             print("\nWARNING: The written solution file corresponds to an INVALID cover.")

    else:
        print("\nAlgorithm failed to find a complete cover for the universe.")
        exit(1)

    print("\n--- Run Finished ---")


if __name__ == "__main__":
    main()