#! /usr/bin/env  python

import os
import re

from utils import normalise_repo_name
from github import Github, GithubException


class GithubMirrorUtils():

	def __init__(self, token=None, tokenfile=None):

		if tokenfile is not None:
			with open(tokenfile, "r") as f:
				self.token = f.read()

		elif token is not None:
			self.token = token

		else:
			raise ValueError("Not token nor tokenfile was passed to the constructor.")


	def print_user_login(self):

		g = Github(self.token)

		print g.get_user().login


	def create_update_mirror_repo(self, org_name, repo_name, src_url, pr_hook_url):

		g = Github(self.token)

		organisation = None
		for org in g.get_user().get_orgs():
			if org_name == org.login:
				organisation = org
				break

		if organisation is None:
			print "Token user is not inside the organisation '{}'".format(org_name)
		else:

			repo = None
			try:
				repo = org.get_repo(repo_name)
				found = True
			except GithubException:
				found = False

			if found:
				print "WARNING: Repo '{}' already exists in the mirror github account".format(repo_name)
			else:
				repo = org.create_repo(repo_name)
				print "Repo '{}' created".format(repo_name)

			self.setup_basic_mirror_repo(repo, src_url, pr_hook_url)
			print "Basc mirror setup completed"

			
	def setup_basic_mirror_repo(self, repo_object, src_url, pr_hook_url):

		desc= "This is a mirror repo. Please fork from {}.".format(src_url)

		repo_object.edit(repo_object.name, description=desc, has_issues=False)


		name = "web"
		config = {"url": pr_hook_url, "content_type": "json"}
		events = ["pull_request"]

		found = False
		for hook in repo_object.get_hooks():
			if hook.config["url"] == pr_hook_url:
				found = True

		if not found:
			repo_object.create_hook(name=name, config=config, events=events)


	def close_pull_request(self, org_name, repo_name, pull_request_number, src_url):

		reply = ("This is a mirror repo and the pull request has been closed automatically.\n"
				"Please, submit your pull request to {}.").format(src_url)

		g = Github(self.token)

		organisation = None
		for org in g.get_user().get_orgs():
			if org_name == org.login:
				organisation = org
				break

		if organisation is None:
			print "Token user is not inside the organisation '{}'".format(org_name)
		else:

			repo = None
			try:
				repo = org.get_repo(repo_name)
				found = True
			except GithubException:
				found = False

			if found:
				pr = repo.get_pull(pull_request_number)
	
				if pr.state != "closed":
					pr.create_issue_comment(reply)
					pr.edit(state="closed")
					print "Pull request with number {} has been closed".format(pull_request_number)
				else:
					print "Pull request with number {} is already closed".format(pull_request_number)
			else:
				print "Repo '{}' not found".format(repo_name)


	def print_org_repos_size(self, org_name):

		g = Github(self.token)

		organisation = None
		for org in g.get_user().get_orgs():
			if org_name == org.login:
				organisation = org
				break

		if organisation is None:
			print "Token user is not inside the organisation '{}'".format(org_name)
		else:
			repo_count = 0
			total_size = 0

			for repo in organisation.get_repos():
				repo_count += 1
				total_size += repo.size
				print "{}({} KB)".format(repo.name, repo.size)

		print "Number of repos: \t{}\nTotal size (KB):\t{}".format(repo_count, total_size)
