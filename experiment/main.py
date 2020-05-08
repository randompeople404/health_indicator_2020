import numpy as np
import time
import os
from experiment.learner_untuned import *
from experiment.learner_tuned import *
from data.data_ready import *
from experiment.runner import *

# metrics: "0" for MRE, "1" for SA
# goal: "0" for commits, "1" for contributors, "2" for stargazer, "3" for open_PRs,
# "4" for closed_PRs, "5" for open_issues, "6" for closed_issues,

repo_pool = []
path = r'../data/data_use/'
for filename in os.listdir(path):
    repo_pool.append(os.path.join(filename))

repeats = 1
month_number = [1, 3, 6, 12]

time_begin = time.time()

for month in month_number:
    for metrics in range(2):
        for goal in range(7):
            for repo in repo_pool:
                print(repo)
                nine_method(repo, path, metrics, repeats, goal, month)

run_time = str(time.time() - time_begin)
print(run_time)