#! /usr/bin/env  python

import os
import re

from github import Github, GithubException

def recreate_pull_request(filename):

	#with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"token.txt"), "r") as f:
	#	mirrors_token = f.read()
	mirrors_token = "d5a9b247ab8ebfed9b24b20800e28df20ff17e9d"

	g = Github(mirrors_token)


	for repo in g.get_user().get_repos():
		print repo.name

		if repo.name == 'test':
			repo.edit(name='test2')




normalise_repo_names('../examples/example-pull-request-post.json')