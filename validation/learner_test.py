from experiment.learner_untuned import *
from experiment.learner_tuned import *
from data.data_ready import *
import os


def learner_check(Repo, Directory, metrics, repeats, goal, month):
    data = data_github_monthly(Repo, Directory, goal)

    for way in range(9):

        if way == 0:
            list_temp = []
            for way in range(repeats):
                list_temp.append(KNN(data, month)[metrics])

            flat_list = np.array(list_temp).flatten()
            list_output = sorted(flat_list.tolist())

            print("median for KNN:", np.median(list_output))

        if way == 1:
            list_temp = []
            for way in range(repeats):
                list_temp.append(SVM(data, month)[metrics])

            flat_list = np.array(list_temp).flatten()
            list_output = sorted(flat_list.tolist())

            print("median for SVR:", np.median(list_output))

        if way == 2:
            list_temp = []
            for way in range(repeats):
                list_temp.append(RFT(data, month)[metrics])

            flat_list = np.array(list_temp).flatten()
            list_output = sorted(flat_list.tolist())

            print("median for RFT:", np.median(list_output))

        if way == 3:
            list_temp = []
            for way in range(repeats):
                list_temp.append(LNR(data, month)[metrics])

            flat_list = np.array(list_temp).flatten()
            list_output = sorted(flat_list.tolist())

            print("median for LNR:", np.median(list_output))

        if way == 4:
            list_temp = []
            for way in range(repeats):
                list_temp.append(CART(data, month)[metrics])

            flat_list = np.array(list_temp).flatten()
            list_output = sorted(flat_list.tolist())

            print("median for CART:", np.median(list_output))

        if way == 5:
            list_temp = []
            for way in range(repeats):
                list_temp.append(GBT(data, month)[metrics])

            flat_list = np.array(list_temp).flatten()
            list_output = sorted(flat_list.tolist())

            print("median for GBT:", np.median(list_output))

        if way == 6:
            list_temp = []
            for way in range(repeats):
                list_temp.append(LGR(data, month)[metrics])

            flat_list = np.array(list_temp).flatten()
            list_output = sorted(flat_list.tolist())

            print("median for LGR:", np.median(list_output))

        if way == 7:
            list_temp = []
            for way in range(repeats):
                list_temp.append(CART_DE(data, metrics, month))

            flat_list = np.array(list_temp).flatten()
            list_output = sorted(flat_list.tolist())

            print("median for CTDE:", np.median(list_output))

        if way == 8:
            list_temp = []
            for way in range(repeats):
                list_temp.append(CART_FLASH(data, metrics, month))

            flat_list = np.array(list_temp).flatten()
            list_output = sorted(flat_list.tolist())

            print("median for ROME:", np.median(list_output))


# goal: "0" for commits, "1" for contributors, "2" for stargazer, "3" for open_PRs,
# "4" for closed_PRs, "5" for open_issues, "6" for closed_issues,


# path = r'../data/data_use/'
# repo = "cantata_monthly.csv"

# Bug point:
# learner_check(repo, path, metrics=0, repeats=1, goal=1, month=1)


if __name__ == '__main__':

    path = r'../data/data_use/'
    repo = "project_data (1).csv"
    # path = r'../data/data_use/'
    # repo = "cantata_monthly.csv"
    # Bug point:
    learner_check(repo, path, metrics=0, repeats=1, goal=1, month=1)
