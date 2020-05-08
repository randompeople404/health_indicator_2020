import pdb
import sys
import os
import time
import random
import traceback
from time import sleep
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd
from pathos.threading import ThreadPool as ThPool
from pathos.multiprocessing import ProcessPool as ProPool

from github import Github
from utils import get_repo_names
from utils import get_existing_results
from utils import get_commits_from_clone_repo
from utils import check_in_problem_repo
from utils import write_problem_repo

OUTPUT_PATH = "./results/"
random_time = [60, 179, 110, 80, 200, 250, 300, 400]
QUOTA_LIMIT = 100


class Miner:
    def __init__(self, user_token, debug=False, num_workers=1, batch_size=200, use_clone=True):
        self.g = Github(user_token, per_page=100)
        self.debug_counts = 200 if debug else 0
        self.results = None
        self.num_workers = num_workers
        self.batch_size = batch_size
        self.use_clone = use_clone

    def get_rate_limit(self, func_name, quota_need):
        remaining = self.g.rate_limiting
        print(f"{self.repo_name}, Running {func_name}, Rate limit: {remaining}")

        start = time.time()
        while self.g.rate_limiting[0] < quota_need:
            delay = random.choice(random_time)
            print(f"{self.repo_name},  Delay {delay} sec")
            sleep(delay)

        elapse = time.time() - start
        if elapse > 100:
            print(f"Wait {elapse / 60} minutes!")

    def get_data(self, repo_name, debug=True):
        self.repo_name = repo_name
        self.output_folder = self._create_output_folder()
        self.repo = self.g.get_repo(repo_name)

        actions = [self._get_commits, self._get_pull_requests,
                   self._get_issues, self._get_stargazers,
                   self._get_forks, self._get_watchers, self.save_results]

        for act in actions:
            act()

    def save_results(self):
        self.results.to_csv(
            OUTPUT_PATH + f"{self.repo_name.split('/')[-1]}_monthly.csv", index=False
        )

    def _get_results_by_threading(self, func, params):
        """
        Query github API by multithreading.
        return a list containing all results.
        """
        num_workers = self.num_workers
        if func.__name__ not in ["multi_pulls", "multi_commits", "multi_watchers"]:
            num_workers = 1;
        if self.debug_counts:
            p = ThPool(num_workers)
            pool_args = params[: self.debug_counts]
            return p.map(func, pool_args)
        else:
            stats = []
            start = time.time()
            for i in range(int(params.totalCount / self.batch_size) + 1):
                if self.num_workers != 1 and i != 0 and (i + 1) * self.batch_size % 800 == 0:
                    print("Sleep 30 sec")
                    sleep(30)
                p = ThPool(num_workers)
                temp = p.map(func, params[i * self.batch_size:(i + 1) * self.batch_size])
                stats += temp
            print(f"{self.repo_name}, {func.__name__} takes: {round(time.time() - start, 3)} secs")
        return stats

    def _create_output_folder(self):
        result_path = OUTPUT_PATH + self.repo_name.split("/")[-1]
        os.makedirs(result_path, exist_ok=True)
        return result_path

    # @profile
    def _get_commits(self):
        """
        Get commits activity grouped by week.
        """

        def retreieve_commits(commits_dates):
            stats = []
            for commit in self.repo.get_commits():
                one = {"commit_id": commit.sha}
                one["committer_id"] = commit.author.login if commit.author else "None"
                one["committed_at"] = commits_dates[commit.sha][0]
                stats.append(one)
            return stats

        commits_dates = get_commits_from_clone_repo(self.repo_name)
        stats = retreieve_commits(commits_dates)  # get commits dates by clone repo

        stats_pd = pd.DataFrame.from_records(stats)
        stats_pd.committed_at = stats_pd.committed_at.astype("datetime64[ns]")
        start_date, end_date = (
            str(stats_pd.committed_at.min())[:7],
            str(stats_pd.committed_at.max())[:7],
        )  # i.e, 2019-09

        new_pd = pd.DataFrame(
            {"dates": pd.date_range(start=start_date, end=end_date, freq="MS")}
        )
        new_pd["monthly_commits"] = 0
        new_pd["monthly_commit_comments"] = 0
        new_pd["monthly_contributors"] = 0

        # fmt:off
        for i in range(len(new_pd)):
            if i != len(new_pd) - 1:
                mask = (stats_pd.committed_at >= new_pd.dates[i]) & (
                        stats_pd.committed_at < new_pd.dates[i + 1]
                )
            else:
                mask = stats_pd.committed_at >= new_pd.dates[i]
            # new_pd.at[i, "monthly_commit_comments"] = sum(stats_pd[mask].commit_comment)
            new_pd.at[i, "monthly_commits"] = len(stats_pd[mask])
            new_pd.at[i, "monthly_contributors"] = len(stats_pd[mask].committer_id.unique())
            if self.debug_counts:
                print(stats_pd[mask].committer_id.unique())
        # fmt:on

        self.results = new_pd.copy()
        csv_file_name = f"{self.repo_name.split('/')[-1]}_commits_and_comments.csv"
        path = os.path.join(self.output_folder, csv_file_name)
        stats_pd.to_csv(
            path,
            index=False,
            columns=["commit_id", "committer_id", "committed_at", "commit_comment"],
        )

    # @profile
    def _get_issues(self, state="all"):  # Total time: 1.4058 s for debug
        """
        Get all the issues from this repo.
        In the csv file, we have the following cols:

        issue_id, state(open/closed), comments(int), created_at, closed_at

        """

        def multi_issues(issue):
            one = {"id": str(issue.number)}
            one["state"] = issue.state
            one["comments"] = issue.comments
            one["created_at"] = str(issue._created_at.value)
            one["closed_at"] = (
                str(issue._closed_at.value)
                if issue._closed_at.value
                else str(pd.to_datetime(1))
            )  # set not closed issue date to 1970-01-01 for calcualte monthly closed issues.
            one["title"] = str(issue.title)
            return one

        all_issues = self.repo.get_issues(state=state)
        stats = self._get_results_by_threading(multi_issues, all_issues)

        stats_pd = pd.DataFrame.from_records(stats)
        stats_pd.created_at = stats_pd.created_at.astype("datetime64[ns]")
        stats_pd.closed_at = stats_pd.closed_at.astype(
            "datetime64[ns]", errors="ignore"
        )

        self.results["monthly_open_issues"] = 0
        self.results["monthly_closed_issues"] = 0
        self.results["monthly_issue_comments"] = 0  # comments from open + closed issues

        for i in range(len(self.results)):
            if i != len(self.results) - 1:
                open_mask = (
                        (stats_pd.created_at >= self.results.dates[i])
                        & (stats_pd.created_at < self.results.dates[i + 1])
                        & (stats_pd.state == "open")
                )
                closed_mask = (
                        (stats_pd.closed_at >= self.results.dates[i])
                        & (stats_pd.closed_at < self.results.dates[i + 1])
                        & (stats_pd.state == "closed")
                )
            else:
                open_mask = (stats_pd.created_at >= self.results.dates[i]) & (
                        stats_pd.state == "open"
                )
                closed_mask = (stats_pd.closed_at >= self.results.dates[i]) & (
                        stats_pd.state == "closed"
                )
            self.results.at[i, "monthly_open_issues"] = len(stats_pd[open_mask])
            self.results.at[i, "monthly_closed_issues"] = len(stats_pd[closed_mask])
            self.results.at[i, "monthly_issue_comments"] = sum(
                stats_pd[open_mask].comments
            ) + sum(
                stats_pd[closed_mask].comments
            )  # comments on both open + closed issues.

        csv_file_name = f"{self.repo_name.split('/')[-1]}_issues.csv"
        path = os.path.join(self.output_folder, csv_file_name)
        stats_pd.to_csv(path, index=False,
                        columns=["id", "created_at", "closed_at", "state", "comments", "title"])

    # @profile
    def _get_stargazers(self):  # Total time: 0.811028 s for debug
        """
        Get monthly stargazers and update it in self.results, will finally save to .csv file
        """
        stargazer = self.repo.get_stargazers_with_dates()
        stats = []
        counts = self.debug_counts
        for star in stargazer:
            if self.debug_counts:
                counts -= 1
                if counts == 0:
                    break
            one = {"user_id": star.user.login}
            one["starred_at"] = star.starred_at
            stats.append(one)

        stats_pd = pd.DataFrame.from_records(stats)
        stats_pd.sort_values(by=["starred_at"])

        self.results["monthly_stargazer"] = 0
        for i in range(len(self.results)):
            if i != len(self.results) - 1:
                mask = (stats_pd.starred_at >= self.results.dates[i]) & (
                        stats_pd.starred_at < self.results.dates[i + 1]
                )
            else:
                mask = stats_pd.starred_at >= self.results.dates[i]
            self.results.at[i, "monthly_stargazer"] = len(stats_pd[mask])

        csv_file_name = f"{self.repo_name.split('/')[-1]}_stargazer.csv"
        path = os.path.join(self.output_folder, csv_file_name)
        stats_pd.to_csv(path, index=False, columns=["starred_at", "user_id"])

    # @profile
    def _get_forks(self):  # Total time: 2.84025 s for debug
        """
        Get monthly forks and update it in self.results, will finally save to .csv file
        """
        forks = self.repo.get_forks()
        stats = []
        counts = self.debug_counts
        for fork in forks:  # this line takes 90.1% time of this function
            if self.debug_counts:
                counts -= 1
                if counts == 0:
                    break
            one = {"user_id": fork.owner.login}
            one["created_at"] = fork.created_at
            stats.append(one)

        stats_pd = pd.DataFrame.from_records(stats)
        stats_pd.sort_values(by=["created_at"])

        self.results["monthly_forks"] = 0
        for i in range(len(self.results)):
            if i != len(self.results) - 1:
                mask = (stats_pd.created_at >= self.results.dates[i]) & (
                        stats_pd.created_at < self.results.dates[i + 1]
                )
            else:
                mask = stats_pd.created_at >= self.results.dates[i]
            self.results.at[i, "monthly_forks"] = len(stats_pd[mask])

        csv_file_name = f"{self.repo_name.split('/')[-1]}_forks.csv"
        path = os.path.join(self.output_folder, csv_file_name)
        stats_pd.to_csv(path, index=False, columns=["created_at", "user_id"])

    # @profile
    def _get_watchers(self):  # Total time: 4.25912 s for debug before multithread=
        """
        Get number of watchers. Each watcher requires a API call.
        # for debug
        Before multithreading, Total time: 4.25912 s
        After multithreading, Total time: 1.125 s
        """

        def multi_watchers(watcher):
            one = {"user_id": watcher.login}
            # created_at line takes 79.0% time of this function
            one["created_at"] = watcher.created_at
            return one

        watchers = self.repo.get_subscribers()  # <---- this strange get_watchers!!
        stats = self._get_results_by_threading(multi_watchers, watchers)

        stats_pd = pd.DataFrame.from_records(stats)
        stats_pd.sort_values(by=["created_at"])

        self.results["monthly_watchers"] = 0
        for i in range(len(self.results)):
            if i != len(self.results) - 1:
                mask = (stats_pd.created_at >= self.results.dates[i]) & (
                        stats_pd.created_at < self.results.dates[i + 1]
                )
            else:
                mask = stats_pd.created_at >= self.results.dates[i]
            self.results.at[i, "monthly_watchers"] = len(stats_pd[mask])

        csv_file_name = f"{self.repo_name.split('/')[-1]}_watchers.csv"
        path = os.path.join(self.output_folder, csv_file_name)
        stats_pd.to_csv(path, index=False, columns=["created_at", "user_id"])

    # @profile
    def _get_pull_requests(self, state="all"):  # Total time: 192.765 s for debug
        """
        Get all the PR from this repo. Note that issues and PR share the same ID system.
        In the csv file, we have the following cols:

        PR_id, state(open/closed), comments, created_at, closed_at, merged, merged_at,

        """
        pulls = self.repo.get_pulls(state=state, sort="created", base="master")
        stats = []

        def multi_pulls(pr):
            one = {"id": str(pr.number)}
            one["state"] = pr.state
            ## FIXME pr.comments line takes 91.4% time of this function, this will call API once!
            one["comments"] = (pr.comments)
            one["created_at"] = str(pr.created_at)
            # set not closed pr date to 1970-01-01 for calcualte monthly stats
            one["closed_at"] = (
                str(pr.closed_at) if pr.closed_at else str(pd.to_datetime(1))
            )
            one["merged"] = bool(pr._merged.value)
            # set not merged pr date to 1970-01-01 for calcualte monthly stats.
            one["merged_at"] = (
                str(pr.merged_at) if pr.merged_at else str(pd.to_datetime(1))
            )
            one["merged_by"] = str(pr.merged_by.login) if pr.merged_by else None
            return one

        stats = self._get_results_by_threading(multi_pulls, pulls)
        stats_pd = pd.DataFrame.from_records(stats)
        stats_pd.created_at = stats_pd.created_at.astype("datetime64[ns]")
        stats_pd.closed_at = stats_pd.closed_at.astype("datetime64[ns]", errors="ignore")
        stats_pd.merged_at = stats_pd.merged_at.astype("datetime64[ns]", errors="ignore")

        self.results["monthly_open_PRs"] = 0
        self.results["monthly_closed_PRs"] = 0
        self.results["monthly_merged_PRs"] = 0
        self.results["monthly_PR_mergers"] = 0
        self.results["monthly_PR_comments"] = 0  # comments from open + closed issues

        for i in range(len(self.results)):
            if i != len(self.results) - 1:
                open_mask = (stats_pd.created_at >= self.results.dates[i]) & (
                        stats_pd.created_at < self.results.dates[i + 1]
                )
                closed_mask = (
                        (stats_pd.closed_at >= self.results.dates[i])
                        & (stats_pd.closed_at < self.results.dates[i + 1])
                        & (stats_pd.state == "closed")
                        & (stats_pd.merged == False)
                )  # all merged PR's state = close, so have to get rid of merged.
                merged_mask = (
                        (stats_pd.closed_at >= self.results.dates[i])
                        & (stats_pd.closed_at < self.results.dates[i + 1])
                        & (stats_pd.merged)
                )
            else:
                open_mask = stats_pd.created_at >= self.results.dates[i]
                closed_mask = (
                        (stats_pd.closed_at >= self.results.dates[i])
                        & (stats_pd.state == "closed")
                        & (stats_pd.merged == False)
                )
                merged_mask = (stats_pd.closed_at >= self.results.dates[i]) & (
                    stats_pd.merged
                )
            self.results.at[i, "monthly_open_PRs"] = len(stats_pd[open_mask])
            self.results.at[i, "monthly_closed_PRs"] = len(stats_pd[closed_mask])
            self.results.at[i, "monthly_merged_PRs"] = len(stats_pd[merged_mask])
            self.results.at[i, "monthly_PR_mergers"] = len(
                stats_pd[merged_mask].merged_by.unique()
            )
            self.results.at[i, "monthly_PR_comments"] = (
                    sum(stats_pd[open_mask].comments)
                    + sum(stats_pd[closed_mask].comments)
                    + sum(stats_pd[merged_mask].comments)
            )  # num of comments on open + closed + merged PRs.

        csv_file_name = f"{self.repo_name.split('/')[-1]}_pr.csv"
        path = os.path.join(self.output_folder, csv_file_name)
        stats_pd.to_csv(path, index=False,
                        columns=[
                            "id",
                            "created_at",
                            "closed_at",
                            "merged_at",
                            "state",
                            "comments",
                            "merged"
                        ]
                        )


_token = {
    "A": "XXX",
    "B": "XXX",
    "C": "XXX",
    "D": "XXX",
    "E": "XXX",
    "F": "XXX",
    "G": "XXX",
    "H": "XXX",
    "I": "XXX",
    "J": "XXX"}

if __name__ == "__main__":
    if len(sys.argv) != 2:
        assert ("Pass token index!")
    token_idx = int(sys.argv[1])
    repo_names = get_repo_names("./data/repo_list3.csv", token_idx, len(_token))
    existing_results = get_existing_results("./results/")

    val = len(repo_names)
    print(f"total repos: {val}")
    print(f"token_idx: {token_idx}")
    token = list(_token.values())[token_idx]

    for repo_name in sorted(repo_names):
        sub_name = repo_name.split("/")[-1]
        if sub_name in existing_results:
            # print(f"{repo_name} exists, skipping...")
            continue
        if check_in_problem_repo(repo_name):
            # print(f"{repo_name} has a problem, found in problem_repo.txt, skipping...")
            continue
        miner = Miner(token, debug=False)
        if miner.g.rate_limiting[0] < QUOTA_LIMIT:
            # sleep(random.choice(random_time))
            print(f"{repo_name}: token is not ready...")
            break
            # miner = Miner(token, debug=False)

        print(f"{repo_name}: start...")
        try:
            error_message = miner.get_data(repo_name)
        except Exception:
            write_problem_repo(repo_name)
            print(f"{miner.repo_name} has errors...")
            traceback.print_exc()
            continue


