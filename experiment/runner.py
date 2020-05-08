import numpy as np
import time
from experiment.learner_untuned import *
from experiment.learner_tuned import *
from data.data_ready import *
import os


def nine_method(Repo, Directory, metrics, repeats, goal, month):
    data = data_github_monthly(Repo, Directory, goal)

    for way in range(8):

        if way == 0:
            list_temp = []
            for i in range(repeats):
                list_temp.append(KNN(data, month)[metrics])

            flat_list = np.array(list_temp).flatten()
            list_output = sorted(flat_list.tolist())

            print("median for KNN:", np.median(list_output))

            with open("../result_experiment/n{}g{}m{}.txt".format(month, goal, metrics), "a+") as output:
                output.write("REPO %s, " % Repo)
                output.write(str(np.median(list_output)) + ",")

        if way == 1:
            list_temp = []
            for i in range(repeats):
                list_temp.append(LNR(data, month)[metrics])

            flat_list = np.array(list_temp).flatten()
            list_output = sorted(flat_list.tolist())

            print("median for LNR:", np.median(list_output))

            with open("../result_experiment/n{}g{}m{}.txt".format(month, goal, metrics), "a+") as output:
                output.write(str(np.median(list_output)) + ",")

        # if way == 2:
        #     list_temp = []
        #     for i in range(repeats):
        #         list_temp.append(LGR(data, month)[metrics])
        #
        #     flat_list = np.array(list_temp).flatten()
        #     list_output = sorted(flat_list.tolist())
        #
        #     print("median for LGR:", np.median(list_output))
        #
        #     with open("../result_experiment/n{}g{}m{}.txt".format(month, goal, metrics), "a+") as output:
        #         output.write(str(np.median(list_output)) + ",")

        if way == 2:
            list_temp = []
            for i in range(repeats):
                list_temp.append(SVM(data, month)[metrics])

            flat_list = np.array(list_temp).flatten()
            list_output = sorted(flat_list.tolist())

            print("median for SVR:", np.median(list_output))

            with open("../result_experiment/n{}g{}m{}.txt".format(month, goal, metrics), "a+") as output:
                output.write(str(np.median(list_output)) + ",")

        if way == 3:
            list_temp = []
            for i in range(repeats):
                list_temp.append(RFT(data, month)[metrics])

            flat_list = np.array(list_temp).flatten()
            list_output = sorted(flat_list.tolist())

            print("median for RFT:", np.median(list_output))

            with open("../result_experiment/n{}g{}m{}.txt".format(month, goal, metrics), "a+") as output:
                output.write(str(np.median(list_output)) + ",")

        if way == 4:
            list_temp = []
            for i in range(repeats):
                list_temp.append(GBT(data, month)[metrics])

            flat_list = np.array(list_temp).flatten()
            list_output = sorted(flat_list.tolist())

            print("median for GBT:", np.median(list_output))

            with open("../result_experiment/n{}g{}m{}.txt".format(month, goal, metrics), "a+") as output:
                output.write(str(np.median(list_output)) + ",")

        if way == 5:
            list_temp = []
            for i in range(repeats):
                list_temp.append(CART(data, month)[metrics])

            flat_list = np.array(list_temp).flatten()
            list_output = sorted(flat_list.tolist())

            print("median for CART:", np.median(list_output))

            with open("../result_experiment/n{}g{}m{}.txt".format(month, goal, metrics), "a+") as output:
                output.write(str(np.median(list_output)) + ",")

        if way == 6:
            list_temp = []
            for i in range(repeats):
                list_temp.append(CART_DE(data, metrics, month))

            flat_list = np.array(list_temp).flatten()
            list_output = sorted(flat_list.tolist())

            print("median for CTDE:", np.median(list_output))

            with open("../result_experiment/n{}g{}m{}.txt".format(month, goal, metrics), "a+") as output:
                output.write(str(np.median(list_output)) + ",")

        if way == 7:
            list_temp = []
            for i in range(repeats):
                list_temp.append(CART_FLASH(data, metrics, month))

            flat_list = np.array(list_temp).flatten()
            list_output = sorted(flat_list.tolist())

            print("median for ROME:", np.median(list_output))

            with open("../result_experiment/n{}g{}m{}.txt".format(month, goal, metrics), "a+") as output:
                output.write(str(np.median(list_output)) + "\n")


if __name__ == '__main__':

    repo_pool = []
    path = r'../data/data_use/'
    for filename in os.listdir(path):
        repo_pool.append(os.path.join(filename))

    Metrics = 0  # "0" for MRE, "1" for SA
    Repeats = 1
    Goal = 1  # "0" for commits, "1" for contributors, "2" for stargazer, "3" for open_PRs,
    # "4" for closed_PRs, "5" for open_issues, "6" for closed_issues,
    month = 1

    for repo in repo_pool:
        print(repo)
        nine_method(repo, path, Metrics, Repeats, Goal, month)