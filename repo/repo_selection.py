import requests
import json
from time import sleep
import sys
from datetime import datetime

headers = {"Authorization": "token xxx"}

# The GraphQL query (with a few aditional bits included) itself defined as a multi-line string.
query1 = """
{
  viewer {
    login
  }
  rateLimit {
    limit
    cost
    remaining
    resetAt
  }
}
"""
query_limit = 1000

### settings
repoFirst = 10
beginDate1 = "2015-01-01T00:00:00Z"
beginDate2 = "2015-09-01T00:00:00Z"
beginDate3 = "2016-05-01T00:00:00Z"

recentDate = "2020-03-20T00:00:00Z"
recentPR = 1

subQueries_1 = {
    "queryString": "is:public archived:false mirror:false created:2015-01-01..2015-08-31 stars:1000..20000 size:>=10000 forks:>=10",
    "repoFirst": repoFirst, "beginDate": beginDate1, "recentDate": recentDate, "recentPR": recentPR}
subQueries_2 = {
    "queryString": "is:public archived:false mirror:false created:2015-09-01..2016-04-30 stars:1000..20000 size:>=10000 forks:>=10",
    "repoFirst": repoFirst, "beginDate": beginDate2, "recentDate": recentDate, "recentPR": recentPR}
subQueries_3 = {
    "queryString": "is:public archived:false mirror:false created:2016-05-01..2016-12-31 stars:1000..20000 size:>=10000 forks:>=10",
    "repoFirst": repoFirst, "beginDate": beginDate3, "recentDate": recentDate, "recentPR": recentPR}


first_query = """
query{{
rateLimit {{
    remaining
    resetAt
}}
search(query:"{queryString}", type: REPOSITORY, first:{repoFirst}) {{
repositoryCount
pageInfo {{
  hasNextPage
  endCursor
}}
edges {{
  node {{
    ... on Repository {{
      url
      total_pr_closed: pullRequests(states: [CLOSED, MERGED]) {{
        totalCount
      }}
      recent_pr: pullRequests(first: {recentPR}, orderBy: {{field: CREATED_AT, direction: DESC}}) {{
        totalCount
        edges {{
          node {{
            ... on PullRequest {{
              createdAt
            }}
          }}
        }}
      }}

      total_issues_closed: issues(states: CLOSED) {{
        totalCount
      }}

      assignableUsers {{
        totalCount
      }}

      defaultBranchRef {{
        name
        target {{
          ... on Commit {{
            recent_commit: history(since: "{recentDate}") {{
              totalCount
            }}
            total_commit: history(since: "{beginDate}"){{
              totalCount
            }}
          }}
        }}
      }}
    }}
  }}
}}
}}
}}
"""

following_query = """
query{{
rateLimit {{
    remaining
    resetAt
}}
search(query:"{queryString}", type: REPOSITORY, first:{repoFirst}, after:"{endCursor}") {{
repositoryCount
pageInfo {{
  hasNextPage
  endCursor
}}
edges {{
  node {{
    ... on Repository {{
      url
      total_pr_closed: pullRequests(states: [CLOSED, MERGED]) {{
        totalCount
      }}
      recent_pr: pullRequests(first: {recentPR}, orderBy: {{field: CREATED_AT, direction: DESC}}) {{
        totalCount
        edges {{
          node {{
            ... on PullRequest {{
              createdAt
            }}
          }}
        }}
      }}

      total_issues_closed: issues(states: CLOSED) {{
        totalCount
      }}

      assignableUsers {{
        totalCount
      }}

      defaultBranchRef {{
        name
        target {{
          ... on Commit {{
            recent_commit: history(since: "{recentDate}") {{
              totalCount
            }}
            total_commit: history(since: "{beginDate}"){{
              totalCount
            }}
          }}
        }}
      }}
    }}
  }}
}}
}}
}}
"""


# In REST, HTTP verbs determine the operation performed. In GraphQL, you'll provide a JSON-encoded body whether you're performing a query or a mutation, so the HTTP verb is POST. The exception is an introspection query, which is a simple GET to the endpoint.
def run_query(query):  # A simple function to use requests.post to make the API call. Note the json= section.
    request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
    print("request return code - {}".format(request.status_code))
    if request.status_code == 200:
        return request.json()
    else:
        tries = 5
        while request.status_code != 200 and tries > 0:
            print("sleep {} min".format(6 - tries))
            sleep((6 - tries) * 60)

            request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
            tries -= 1
            print("Retry {} th".format(6 - tries))
        if request.status_code == 200:
            return request.json()
        else:
            print("request return code - {}".format(request.status_code))
            print(request.content)
            raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))


def checkTokenLimit():
    result = run_query(query1)  # Execute the query
    remaining_rate_limit = result["data"]["rateLimit"]["remaining"]  # Drill down the dictionary
    print("Remaining rate limit - {}".format(remaining_rate_limit))

    resetTime = result["data"]["rateLimit"]["resetAt"]
    print("GitHub API must be reset to time - {}".format(resetTime))

    resetTime = datetime.strptime(resetTime, '%Y-%m-%dT%H:%M:%SZ')
    nowTimeUTC = datetime.utcnow()
    print("UTC time now - {}".format(nowTimeUTC))
    if nowTimeUTC.date() == resetTime.date() and nowTimeUTC.time() < resetTime.time():
        print("will reset in future")
        return remaining_rate_limit
    else:
        raise Exception("resetAt error")


def getFirstQuerySearch(variables):
    return first_query.format(**variables)


def getFollowingQuerySearch(variables, endCursor):
    variables["endCursor"] = endCursor
    return following_query.format(**variables)


def filterRepo(repoInfo):
    """
    total_issue_closed:>=50
    total_PR_closed:>=50
    recent_PR:>=1
    total_commit:>=1000
    recent_commit:>=1
    """
    total_pr_closed, total_issues_closed = repoInfo["total_pr_closed"]["totalCount"], repoInfo["total_issues_closed"][
        "totalCount"]
    if total_pr_closed < 50 or total_issues_closed < 50:
        return repoInfo["url"], False

    total_commit, recent_commit = repoInfo["defaultBranchRef"]["target"]["total_commit"]["totalCount"], \
                                  repoInfo["defaultBranchRef"]["target"]["recent_commit"]["totalCount"]
    if total_commit < 1000 or recent_commit == 0:
        return repoInfo["url"], False

    # assignable_users=repoInfo["assignableUsers"]["totalCount"]
    # if assignable_users<3:
    #     return repoInfo["url"],False

    recent_pr = repoInfo["recent_pr"]["edges"][recentPR - 1]
    recent_pr_createdAt = recent_pr["node"]["createdAt"]
    if recent_pr_createdAt < recentDate:
        return repoInfo["url"], False

    return repoInfo["url"], True


def filterRepos(repos):
    valid_urls, invalid_urls = [], []
    for info in repos:
        url, isValid = filterRepo(info['node'])
        if isValid:
            valid_urls.append(url)
        else:
            invalid_urls.append(url)
    return valid_urls, invalid_urls


def getRepoUrls(subquery, filename_valid, filename_invalid):
    valids, invalids = [], []
    query = getFirstQuerySearch(subquery)
    # print(query)
    result = run_query(query)
    count = 1

    total = result['data']['search']['repositoryCount']
    print(subquery["queryString"], "total urls:", total)

    data = result['data']['search']["edges"]
    valid_urls, invalid_urls = filterRepos(data)
    valids.extend(valid_urls)
    invalids.extend(invalid_urls)

    lastCursor = result['data']['search']['pageInfo']['endCursor']
    hasNextPage = result['data']['search']['pageInfo']['hasNextPage']
    print("endCursor:", lastCursor, " count: ", count)

    while hasNextPage:
        query = getFollowingQuerySearch(subquery, endCursor=lastCursor)
        result = run_query(query)
        count += 1
        if "errors" in result:
            print(query)
            print(result)
            raise Exception("error in processing query: " + subquery + " iteration: " + str(count))

        data = result['data']['search']["edges"]
        valid_urls, invalid_urls = filterRepos(data)
        valids.extend(valid_urls)
        invalids.extend(invalid_urls)

        lastCursor = result['data']['search']['pageInfo']['endCursor']
        hasNextPage = result['data']['search']['pageInfo']['hasNextPage']
        print("endCursor:", lastCursor, " count: ", count)

        remain_token = result["data"]["rateLimit"]["remaining"]
        print("remain token - {}".format(remain_token))
        if remain_token < 5:
            sleep(3600)
            while checkTokenLimit() < 4000:
                sleep(60)

    with open(filename_valid, 'w') as f:
        for item in valids:
            f.write("%s\n" % item)

    with open(filename_invalid, 'w') as f:
        for item in invalids:
            f.write("%s\n" % item)


def checkTokenLimit():
    result = run_query(query1)  # Execute the query
    remaining_rate_limit = result["data"]["rateLimit"]["remaining"]  # Drill down the dictionary
    print("Remaining rate limit - {}".format(remaining_rate_limit))

    resetTime = result["data"]["rateLimit"]["resetAt"]
    print("GitHub API must be reset to time - {}".format(resetTime))

    resetTime = datetime.strptime(resetTime, '%Y-%m-%dT%H:%M:%SZ')
    nowTimeUTC = datetime.utcnow()
    print("UTC time now - {}".format(nowTimeUTC))
    if nowTimeUTC.date() == resetTime.date() and nowTimeUTC.time() < resetTime.time():
        print("will reset in future")
        return remaining_rate_limit
    else:
        raise Exception("resetAt error")


if __name__ == '__main__':
    #     checkTokenLimit()
    print(subQueries_1)
    getRepoUrls(subQueries_1, "valid_1.txt", "invalid_1.txt")

    print(subQueries_2)
    getRepoUrls(subQueries_2, "valid_2.txt", "invalid_2.txt")

    print(subQueries_3)
    getRepoUrls(subQueries_3, "valid_3.txt", "invalid_3.txt")
