from experiment.learner_untuned import *
from experiment.learner_tuned import *
from data.data_ready import *
# from sklearn.tree.export import export_text
from sklearn.tree import export_text
import os

def CARTT(dataset, month, a=12, b=1, c=2):

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

    r = export_text(model, feature_names=list(train_input.columns.values))[1]
    # print(r)
    feature_used = list(dict.fromkeys(r))
    # print(feature_used)
    # tree.plot_tree(model, feature_names=list(train_input.columns.values))
    # plt.show()

    return mre_list, sa_list, feature_used


def cart_feature_check(Repo, Directory, goal, month):
    data = data_github_monthly(Repo, Directory, goal)
    list_temp = CARTT(data, month)[2]
    # print(list_temp)
    return list_temp



repo_pool = []
path = r'../data/data_use/'

# repo = "android-hidden-api_monthly.csv"
# cart_feature_check(repo, path, metrics=0, repeats=1, goal=1, month=1)
goal = 6
# goal: "0" for commits, "1" for contributors, "2" for stargazer, "3" for open_PRs,
# "4" for closed_PRs, "5" for open_issues, "6" for closed_issues,
big_list = []

for filename in os.listdir(path):
    repo_pool.append(os.path.join(filename))
for repo in repo_pool:
    # print(repo)
    big_list.append(cart_feature_check(repo, path, goal, month=1))

commits = 0
issue_comments = 0
open_issues = 0
open_PRs = 0
closed_issues = 0
watchers = 0
PR_comments = 0
contributors = 0
merged_PRs = 0
PR_mergers = 0
closed_PRs = 0
stargazer = 0
forks = 0

for project in big_list:
    for feature in project:
        if feature == 'monthly_commits':
            commits += 1
        elif feature == 'monthly_issue_comments':
            issue_comments += 1
        elif feature == 'monthly_open_issues':
            open_issues += 1
        elif feature == 'monthly_open_PRs':
            open_PRs += 1
        elif feature == 'monthly_closed_issues':
            closed_issues += 1
        elif feature == 'monthly_watchers':
            watchers += 1
        elif feature == 'monthly_PR_comments':
            PR_comments += 1
        elif feature == 'monthly_contributors':
            contributors += 1
        elif feature == 'monthly_merged_PRs':
            merged_PRs += 1
        elif feature == 'monthly_PR_mergers':
            PR_mergers += 1
        elif feature == 'monthly_closed_PRs':
            closed_PRs += 1
        elif feature == 'monthly_stargazer':
            stargazer += 1
        elif feature == 'monthly_forks':
            forks += 1

feature_stats = [commits, contributors, stargazer, open_PRs, closed_PRs, merged_PRs, PR_mergers, PR_comments, open_issues, closed_issues, issue_comments, forks, watchers]

feature_percentage = [round(num/1628, 2) for num in feature_stats]

print(feature_percentage)


# note: below part of code is changed from sklearn.tree.export_text to get node info
# def export_text(decision_tree, feature_names=None, max_depth=10,
#                 spacing=3, decimals=2, show_weights=False):
#     """Build a text report showing the rules of a decision tree.
#
#     Note that backwards compatibility may not be supported.
#
#     Parameters
#     ----------
#     decision_tree : object
#         The decision tree estimator to be exported.
#         It can be an instance of
#         DecisionTreeClassifier or DecisionTreeRegressor.
#
#     feature_names : list, optional (default=None)
#         A list of length n_features containing the feature names.
#         If None generic names will be used ("feature_0", "feature_1", ...).
#
#     max_depth : int, optional (default=10)
#         Only the first max_depth levels of the tree are exported.
#         Truncated branches will be marked with "...".
#
#     spacing : int, optional (default=3)
#         Number of spaces between edges. The higher it is, the wider the result.
#
#     decimals : int, optional (default=2)
#         Number of decimal digits to display.
#
#     show_weights : bool, optional (default=False)
#         If true the classification weights will be exported on each leaf.
#         The classification weights are the number of samples each class.
#
#     Returns
#     -------
#     report : string
#         Text summary of all the rules in the decision tree.
#
#     Examples
#     --------
#
#     >>> from sklearn.datasets import load_iris
#     >>> from sklearn.tree import DecisionTreeClassifier
#     >>> from sklearn.tree import export_text
#     >>> iris = load_iris()
#     >>> X = iris['data']
#     >>> y = iris['target']
#     >>> decision_tree = DecisionTreeClassifier(random_state=0, max_depth=2)
#     >>> decision_tree = decision_tree.fit(X, y)
#     >>> r = export_text(decision_tree, feature_names=iris['feature_names'])
#     >>> print(r)
#     |--- petal width (cm) <= 0.80
#     |   |--- class: 0
#     |--- petal width (cm) >  0.80
#     |   |--- petal width (cm) <= 1.75
#     |   |   |--- class: 1
#     |   |--- petal width (cm) >  1.75
#     |   |   |--- class: 2
#     """
#     ###############
#     temp = []
#
#     ###############
#     check_is_fitted(decision_tree)
#     tree_ = decision_tree.tree_
#     if is_classifier(decision_tree):
#         class_names = decision_tree.classes_
#     right_child_fmt = "{} {} <= {}\n"
#     left_child_fmt = "{} {} >  {}\n"
#     truncation_fmt = "{} {}\n"
#
#     if max_depth < 0:
#         raise ValueError("max_depth bust be >= 0, given %d" % max_depth)
#
#     if (feature_names is not None and
#             len(feature_names) != tree_.n_features):
#         raise ValueError("feature_names must contain "
#                          "%d elements, got %d" % (tree_.n_features,
#                                                   len(feature_names)))
#
#     if spacing <= 0:
#         raise ValueError("spacing must be > 0, given %d" % spacing)
#
#     if decimals < 0:
#         raise ValueError("decimals must be >= 0, given %d" % decimals)
#
#     if isinstance(decision_tree, DecisionTreeClassifier):
#         value_fmt = "{}{} weights: {}\n"
#         if not show_weights:
#             value_fmt = "{}{}{}\n"
#     else:
#         value_fmt = "{}{} value: {}\n"
#
#     if feature_names:
#         feature_names_ = [feature_names[i] if i != _tree.TREE_UNDEFINED
#                           else None for i in tree_.feature]
#     else:
#         feature_names_ = ["feature_{}".format(i) for i in tree_.feature]
#
#     export_text.report = ""
#
#     def _add_leaf(value, class_name, indent):
#         val = ''
#         is_classification = isinstance(decision_tree,
#                                        DecisionTreeClassifier)
#         if show_weights or not is_classification:
#             val = ["{1:.{0}f}, ".format(decimals, v) for v in value]
#             val = '['+''.join(val)[:-2]+']'
#         if is_classification:
#             val += ' class: ' + str(class_name)
#         export_text.report += value_fmt.format(indent, '', val)
#
#     def print_tree_recurse(node, depth):
#         indent = ("|" + (" " * spacing)) * depth
#         indent = indent[:-spacing] + "-" * spacing
#
#         value = None
#         if tree_.n_outputs == 1:
#             value = tree_.value[node][0]
#         else:
#             value = tree_.value[node].T[0]
#         class_name = np.argmax(value)
#
#         if (tree_.n_classes[0] != 1 and
#                 tree_.n_outputs == 1):
#             class_name = class_names[class_name]
#
#         if depth <= max_depth+1:
#             info_fmt = ""
#             info_fmt_left = info_fmt
#             info_fmt_right = info_fmt
#
#             if tree_.feature[node] != _tree.TREE_UNDEFINED:
#                 name = feature_names_[node]
#                 threshold = tree_.threshold[node]
#                 threshold = "{1:.{0}f}".format(decimals, threshold)
#                 export_text.report += right_child_fmt.format(indent,
#                                                              name,
#                                                              threshold)
#                 temp.append(str(name))
#                 export_text.report += info_fmt_left
#                 print_tree_recurse(tree_.children_left[node], depth+1)
#
#                 export_text.report += left_child_fmt.format(indent,
#                                                             name,
#                                                             threshold)
#                 temp.append(str(name))
#                 export_text.report += info_fmt_right
#                 print_tree_recurse(tree_.children_right[node], depth+1)
#             else:  # leaf
#                 _add_leaf(value, class_name, indent)
#         else:
#             subtree_depth = _compute_depth(tree_, node)
#             if subtree_depth == 1:
#                 _add_leaf(value, class_name, indent)
#             else:
#                 trunc_report = 'truncated branch of depth %d' % subtree_depth
#                 export_text.report += truncation_fmt.format(indent,
#                                                             trunc_report)
#
#     print_tree_recurse(0, 1)
#     return export_text.report, temp