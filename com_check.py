import requests
import json
from datetime import datetime, timedelta
import zulu
from dateutil import tz
import pandas as pd
import csv

to_zone = tz.gettz('IST')

last_12_hrs = datetime.now() - timedelta(hours=12)
last_12_hrs = last_12_hrs.astimezone(to_zone)


def get_last_commit(github_url):
    if github_url[-1] == '/':
        github_url = github_url[:-1]
    github_url = str(github_url).split('/')
    username = github_url[-2]
    repo_name = github_url[-1]
    url = f'https://api.github.com/repos/{username}/{repo_name}/branches'
    headers = {'Authorization': f'token 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'}
    response = requests.get(url=url, headers=headers)
    branches = [i["name"] for i in json.loads(response.text)]
    times = []
    for i in branches:
        url = f'https://api.github.com/repos/{username}/{repo_name}/commits/{i}'
        response = requests.get(url=url, headers=headers)
        data_req = json.loads(response.text)['commit']['author']['date']
        times.append(zulu.parse(data_req).datetime.astimezone(to_zone))
    times.sort()
    if times[-1] > last_12_hrs:
        return [True, times[-1]]
    return [False, times[-1]]


data = pd.read_csv('data.csv', header=None)
data = data.values.tolist()

f = open('kick.csv', 'w+', newline='\n')
f2 = open('commited.csv', 'w+', newline='\n')
kick = csv.writer(f)
commit = csv.writer(f2)

for i in data:
    try:
        data = get_last_commit(i[3])
        if data[0] == True:
            i.append(data[1])
            commit.writerow(i)
        else:
            print(i[0])
            i.append(data[1])
            kick.writerow(i)
    except:
        print(i[0])
        i.append('no commits')
        kick.writerow(i)