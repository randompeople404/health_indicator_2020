import numpy as np
from data.data_ready import *
from experiment.utility import *
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import LogisticRegression
from sklearn import svm
from sklearn import neighbors
import pdb


def CART(dataset, month, a=12, b=1, c=2):

    dataset = normalize(dataset)
    mre_list = []
    sa_list = []
    for train, test in df_split(dataset, month):
        train_input = train.iloc[:, :-1]
        train_actual_effort = train.iloc[:, -1]
        test_input = test.iloc[:, :-1]
        test_actual_effort = test.iloc[:, -1]
        # max_depth: [1:12], min_samples_leaf: [1:12], min_samples_split: [2:21]

        model = DecisionTreeRegressor(max_depth=a, min_samples_leaf=b, min_samples_split=c)
        model.fit(train_input, train_actual_effort)
        test_predict_effort = model.predict(test_input)
        test_predict_Y = test_predict_effort
        test_actual_Y = test_actual_effort.values

        mre_list.append(mre_calc(test_predict_Y, test_actual_Y))   ######### for MRE
        sa_list.append(sa_calc(test_predict_Y, test_actual_Y, train_actual_effort))   ######### for SA

    return mre_list, sa_list


def KNN(dataset, month, n_neighbors = 5):

    dataset = normalize(dataset)
    mre_list = []
    sa_list = []
    for train, test in df_split(dataset, month):
        train_input = train.iloc[:, :-1]
        train_actual_effort = train.iloc[:, -1]
        test_input = test.iloc[:, :-1]
        test_actual_effort = test.iloc[:, -1]

        model = neighbors.KNeighborsRegressor(n_neighbors)
        model.fit(train_input, train_actual_effort)
        test_predict_effort = model.predict(test_input)
        test_predict_Y = test_predict_effort
        test_actual_Y = test_actual_effort.values

        mre_list.append(mre_calc(test_predict_Y, test_actual_Y))   ######### for MRE
        sa_list.append(sa_calc(test_predict_Y, test_actual_Y, train_actual_effort))   ######### for SA

    return mre_list, sa_list


def SVM(dataset, month):

    dataset = normalize(dataset)
    mre_list = []
    sa_list = []
    for train, test in df_split(dataset, month):
        train_input = train.iloc[:, :-1]
        train_actual_effort = train.iloc[:, -1]
        test_input = test.iloc[:, :-1]
        test_actual_effort = test.iloc[:, -1]

        model = svm.SVR()
        model.fit(train_input, train_actual_effort)
        test_predict_effort = model.predict(test_input)
        test_predict_Y = test_predict_effort
        test_actual_Y = test_actual_effort.values

        mre_list.append(mre_calc(test_predict_Y, test_actual_Y))   ######### for MRE
        sa_list.append(sa_calc(test_predict_Y, test_actual_Y, train_actual_effort))   ######### for SA

    return mre_list, sa_list


def RFT(dataset, month, max_depth=3):

    dataset = normalize(dataset)
    mre_list = []
    sa_list = []
    for train, test in df_split(dataset, month):
        train_input = train.iloc[:, :-1]
        train_actual_effort = train.iloc[:, -1]
        test_input = test.iloc[:, :-1]
        test_actual_effort = test.iloc[:, -1]

        model = RandomForestRegressor(max_depth)
        model.fit(train_input, train_actual_effort)
        test_predict_effort = model.predict(test_input)
        test_predict_Y = test_predict_effort
        test_actual_Y = test_actual_effort.values

        mre_list.append(mre_calc(test_predict_Y, test_actual_Y))   ######### for MRE
        sa_list.append(sa_calc(test_predict_Y, test_actual_Y, train_actual_effort))   ######### for SA

    return mre_list, sa_list


def LNR(dataset, month):

    dataset = normalize(dataset)
    mre_list = []
    sa_list = []
    for train, test in df_split(dataset, month):
        train_input = train.iloc[:, :-1]
        train_actual_effort = train.iloc[:, -1]
        test_input = test.iloc[:, :-1]
        test_actual_effort = test.iloc[:, -1]

        model = LinearRegression()
        model.fit(train_input, train_actual_effort)
        test_predict_effort = model.predict(test_input)
        test_predict_Y = test_predict_effort
        test_actual_Y = test_actual_effort.values

        mre_list.append(mre_calc(test_predict_Y, test_actual_Y))   ######### for MRE
        sa_list.append(sa_calc(test_predict_Y, test_actual_Y, train_actual_effort))   ######### for SA

    return mre_list, sa_list


def GBT(dataset, month):

    dataset = normalize(dataset)
    mre_list = []
    sa_list = []
    for train, test in df_split(dataset, month):
        train_input = train.iloc[:, :-1]
        train_actual_effort = train.iloc[:, -1]
        test_input = test.iloc[:, :-1]
        test_actual_effort = test.iloc[:, -1]

        model = GradientBoostingRegressor()
        model.fit(train_input, train_actual_effort)
        test_predict_effort = model.predict(test_input)
        test_predict_Y = test_predict_effort
        test_actual_Y = test_actual_effort.values

        mre_list.append(mre_calc(test_predict_Y, test_actual_Y))   ######### for MRE
        sa_list.append(sa_calc(test_predict_Y, test_actual_Y, train_actual_effort))   ######### for SA

    return mre_list, sa_list


def LGR(dataset, month):

    dataset = normalize(dataset)
    mre_list = []
    sa_list = []
    for train, test in df_split(dataset, month):
        train_input = train.iloc[:, :-1]
        train_actual_effort = train.iloc[:, -1]
        test_input = test.iloc[:, :-1]
        test_actual_effort = test.iloc[:, -1]

        model = LogisticRegression()
        model.fit(train_input, train_actual_effort)
        test_predict_effort = model.predict(test_input)
        test_predict_Y = test_predict_effort
        test_actual_Y = test_actual_effort.values

        mre_list.append(mre_calc(test_predict_Y, test_actual_Y))   ######### for MRE
        sa_list.append(sa_calc(test_predict_Y, test_actual_Y, train_actual_effort))   ######### for SA

    return mre_list, sa_list


if __name__ == '__main__':
    listA = []
    path = r'../data/data_use/'
    repo = "project_data (1).csv"
    for i in range(2):
        listA.append(CART(data_github_monthly(repo, path, 1), 1)[0])
    print(np.array(sorted(listA)).flatten())
