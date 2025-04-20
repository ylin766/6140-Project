## 6140-Project

Haoxin Liu, Yushuhong Lin, Weihan Li

### Project Structure

```
├── README.md                           # This file describing the project
    ├── bnb                             # BnB algorithm
        ├── batch_run.py
        ├── bnb.py
    ├── approx                          # Approxiation algorithm
        ├── set_cover_approx.py
        ├── batch_runner.py
    ├── localsearch                     # Two local search algorithm
        ├── ls_algorithms.py    
        ├── eval_ls.py           
        ├── run_ls.py             
    ├── data                            # Data folder
    ├── output                          # Algorithm outputs
```

### BnB algorithm
Run the following command to batch test the BnB algorithm:

```
python batch_run.py --prefix <file_prefix> --start <start_index> --end <end_index>
```

Example:

```
python batch_run.py --prefix large --start 1 --end 12
```

This will automatically run the Branch and Bound (BnB) algorithm on the specified input files.


### Approxiation algorithm

Run the following command to run the approxiation algorithm:

```
python set_cover_approx.py --inst <file_name> --alg <algo_name> --time <cut_off_time> --seed <random_seeds>
```

Example:

```
python set_cover_approx.py -inst data/large1.in -alg Approx -time 600 -seed 0
```
Run the following command to generate all resutls.
```
python batch_runner.py
```

### Local Search algorithm

We implements two local-search variants for the Minimum Set Cover problem:

- **LS1**: Hill-Climbing 
- **LS2**: Simulated Annealing

Run the following command to run the local search algorithm:

```
python run_ls.py --inst <file_name> --alg <algo_name> --time <cut_off_time> --seed <random_seeds>
```

Example:

```
python run_ls.py --inst large1 --alg LS1 --time 60 --seed 1 2 3 4 5
```

Run the following command to generate the result tables and figures:

```
python eval_ls.py --inst <file_name> --alg <algo_name> --time <cut_off_time> --seed <random_seeds>
```

Example:

```
python eval_ls.py --inst large1 --alg LS1 --time 60 --seed 1 2 3 4 5
```
