import os
from statistics import median

import pandas as pd
import numpy as np

path = r'../result_sanity_test/'
filename = "predict_actual_all_month01.txt"
data_size = 1628
itr_size = 40

data_with_candi = pd.read_csv(path + filename, sep=',', header=None)

# print(data_with_candi)
best_predict = -1
best_actual = -1

for i in range(data_size):
    best_abs = 10000
    for j in range(itr_size*i, itr_size*(i+1)):
        if data_with_candi.iloc[j, 2] < best_abs:
            best_predict = data_with_candi.iloc[j, 0]
            best_actual = data_with_candi.iloc[j, 1]
            best_abs = data_with_candi.iloc[j, 2]
    with open("../result_sanity_test/predict_actual_1628_month01.txt", "a+") as output:
        output.write(str(round(best_predict, 4)) + "," + str(best_actual) + "\n")
