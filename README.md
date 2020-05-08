# health_indicator_2020
Data and experiment replication code for ASE2020 submission

## Experiment Replication

To reproduce the experiment results, execute `main.py` in directory `experiments`, you will get all `n{a}g{b}m{c}.txt` file which stores the numeric experiment results in directory `result_experiment`. Here, `a` indicates which month to predict (1,3,6,12), `a` indicates which goal to predict (1-7) and `a` indicates which metrics from prediction (0, 1), the details about these parameters are commented in `main.py`. 

We store all experiment data in directory `data/data_use`, this data is selected using the criteria in `repo/repo_selection.py` (Table 2) and collected using `repo/repo_miner/mining_runner.py`, the stats information (Table 5) of data can be obtained by excuting `data/data_stats.py`.

To represent the results of RQ1, run `stats.py` in directory `experiments`, the results (Table 6-9) are stored in `result_stats/stats.csv`

To represent the results of RQ2, run `internal_feature_select.py` in directory `validation`, to get result in (Table 11), note that our methods use a modified version of `sklearn.tree.export_text`, please see comments in code for details.

To represent the results of RQ3, use the stats results generated in `result_stats/stats.csv` since its information are already collected from `stats.py` (Table 12-13).

For results of predicting mid-lifecycle in Discussion section (Table 14), run `runner.py` in directory `experiments`, and set related data range into `N-24`, please see comments in code for details.
