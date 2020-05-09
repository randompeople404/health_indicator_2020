from experiment.utility import *
from sklearn.tree import DecisionTreeRegressor
from experiment.optimizer import *


def CART_DE(dataset, metrics, month):

    dataset = normalize(dataset)
    mre_list = []
    sa_list = []
    for train, test in df_split(dataset, month):

        train_input = train.iloc[:, :-1]
        train_actual_effort = train.iloc[:, -1]
        test_input = test.iloc[:, :-1]
        test_actual_effort = test.iloc[:, -1]
        # max_depth: [1:12], min_samples_leaf: [1:12], min_samples_split: [2:21]

        def cart_builder(a, b, c):
            model = DecisionTreeRegressor(max_depth=a, min_samples_leaf=b, min_samples_split=c)
            model.fit(train_input, train_actual_effort)
            test_predict_effort = model.predict(test_input)
            test_predict_Y = test_predict_effort
            test_actual_Y = test_actual_effort.values
            # with open("../result_sanity_test/predict_actual_all_month01.txt", "a+") as output:
            #     output.write(str(test_predict_Y[0]) + "," + str(test_actual_Y[0]) + "," + str(abs(test_actual_Y[0] - test_predict_Y[0])) + "\n")

            if metrics == 0:
                return mre_calc(test_predict_Y, test_actual_Y)  ############# MRE
            if metrics == 1:
                return sa_calc(test_predict_Y, test_actual_Y, train_actual_effort)  ############# SA

        output = de(cart_builder, metrics, bounds=[(1, 12), (0.00001, 0.5), (0.00001, 1)])
        if metrics == 0:
            mre_list.append(output)  ############# MRE
        if metrics == 1:
            sa_list.append(output)  ############# SA

    if metrics == 0:
        return mre_list  ############# MRE
    if metrics == 1:
        return sa_list  ############# SA


def CART_FLASH(dataset, metrics, month):
    dataset = normalize(dataset)
    result_list = []

    for train, test in df_split(dataset, month):
        train_input = train.iloc[:, :-1]
        train_actual_effort = train.iloc[:, -1]
        test_input = test.iloc[:, :-1]
        test_actual_effort = test.iloc[:, -1]
        # max_depth: [1:12], min_samples_leaf: [1:12], min_samples_split: [2:21]

        output = flash(train_input, train_actual_effort, test_input, test_actual_effort, metrics, 10)
        result_list.append(output)

    return result_list



if __name__ == '__main__':

    import time
    from data.data_ready import *

    path = r'../data/data_use/'
    repo = "Project0001.csv"

    data = data_github_monthly(repo, path, 1)
    repeats = 20
    list_CART = []

    time1 = time.time()
    for i in range(repeats):
        list_CART.append(CART_FLASH(data, 0, 1))
    run_time1 = str(time.time() - time1)

    flat_list = np.array(list_CART).flatten()
    cart0_output = sorted(flat_list.tolist())

    print(cart0_output)
    print("median for CART0:", np.median(cart0_output))
    # print("mean for CART0:", np.mean(cart0_output))
    print("runtime for CART0:", run_time1)
    #
    # with open("./output/test_sk_mre.txt", "w") as output:
    #     output.write("CART0" + '\n')
    #     for i in sorted(cart0_output):
    #         output.write(str(i)+" ")
