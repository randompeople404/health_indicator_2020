import os
from statistics import median

import pandas as pd
import numpy as np


def repo_stats(filename, path):
    result_raw = pd.read_csv(path + filename, sep=',', header=None)

    result_median = []
    result_q25 = []
    result_q75 = []
    result_iqr = []
    result_std = []
    result_win = [0,0,0,0,0,0,0,0]

    for learner in range (1,9):
        result_median.append(median(result_raw.iloc[:, learner]))
        result_q25.append(result_raw.iloc[:, learner].quantile(.25))
        result_q75.append(result_raw.iloc[:, learner].quantile(.75))
        result_iqr.append(result_raw.iloc[:, learner].quantile(.75) - result_raw.iloc[:, learner].quantile(.25))
        result_std.append(result_raw.iloc[:, learner].std())

    win_range = np.quantile(result_raw.iloc[:,1:9].to_numpy(), 0.424)

    for row in range(len(result_raw)):
        for i in range(8):
            if filename[-5] == "0":
                if result_raw.iloc[row, i+1] > min(result_raw.iloc[row, 1:]) + abs(win_range):
                    result_win[i] += 0
                else:
                    result_win[i] += 1
            elif filename[-5] == "1":
                if result_raw.iloc[row, i+1] < max(result_raw.iloc[row, 1:]) - abs(win_range):
                    result_win[i] += 0
                else:
                    result_win[i] += 1

    result_q25 = [round(num, 3) for num in result_q25]
    result_q75 = [round(num, 3) for num in result_q75]
    result_median = [round(num, 3) for num in result_median]
    result_std = [round(num, 3) for num in result_std]
    result_iqr = [round(num, 3) for num in result_iqr]
    result_win = [round(num, 3) for num in result_win]

    print("25%: ", result_q25)
    print("75%: ", result_q75)
    print("median: ", result_median)
    print("std: ", result_std)
    print("iqr: ", result_iqr)
    print("win: ", result_win)

    # with open("../result_stats/stats_{}".format(filename), "a+") as output:
    with open("../result_stats/stats.csv", "a+") as output:
        output.write(filename+'\n')

        output.write("25%,")
        for i in range(len(result_q25)):
            if i < len(result_q25) - 1:
                output.write(str(result_q25[i]) + ",")
            else:
                output.write(str(result_q25[i]))
        output.write('\n')

        output.write("75%,")
        for i in range(len(result_q75)):
            if i < len(result_q75) - 1:
                output.write(str(result_q75[i]) + ",")
            else:
                output.write(str(result_q75[i]))
        output.write('\n')

        output.write("median,")
        for i in range(len(result_median)):
            if i < len(result_median) - 1:
                output.write(str(result_median[i]) + ",")
            else:
                output.write(str(result_median[i]))
        output.write('\n')

        output.write("std,")
        for i in range(len(result_std)):
            if i < len(result_std) - 1:
                output.write(str(result_std[i]) + ",")
            else:
                output.write(str(result_std[i]))
        output.write('\n')

        output.write("iqr,")
        for i in range(len(result_iqr)):
            if i < len(result_iqr) - 1:
                output.write(str(result_iqr[i]) + ",")
            else:
                output.write(str(result_iqr[i]))
        output.write('\n')

        output.write("win,")
        for i in range(len(result_win)):
            if i < len(result_win) - 1:
                output.write(str(result_win[i]) + ",")
            else:
                output.write(str(result_win[i]))
        output.write('\n')


if __name__ == '__main__':

    path = r'../result_experiment/'
    for filename in os.listdir(path):
        print("------", filename, "------")
        repo_stats(filename, path)

    # KNN, LNR, SVM, RFT, GBT, CART, CTDE, ROME
    # metrics: "0" for MRE, "1" for SA
    # goal: "0" for commits, "1" for contributors, "2" for stargazer, "3" for open_PRs,
    # "4" for closed_PRs, "5" for open_issues, "6" for closed_issues,

    # filename_test01 = "n12g0m1.txt"
    # filename_test02 = "n12g1m1.txt"
    #
    # repo_stats(filename_test01, path)