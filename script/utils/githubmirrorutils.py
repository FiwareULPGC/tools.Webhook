#! /usr/bin/env  python

import os
import re

import urllib2
from utils import normalise_repo_name
from github import Github, GithubException
import requests
from requests.utils import quote


class GithubMirrorUtils():

	def __init__(self, tokenfile=None):

		with open(tokenfile, "r") as f:
			self.token = f.read().strip()

			if self.token is None or self.token == "":
				raise ValueError("File {} is empty".format(tokenfile))


	def print_user_login(self):

		g = Github(self.token)

		print g.get_user().login


	def get_org_object(self, org_name):

		g = Github(self.token)

		organization = None
		for org in g.get_user().get_orgs():
			if org_name == org.login:
				organization = org
				break

		if organization is None:
			print "Token user is not inside the organization '{}'".format(org_name)

		return organization


	def get_repo_object(self, org_name, repo_name):

		organization = self.get_org_object(org_name)
		
		repo = None
		if organization is not None:
			try:
				repo = organization.get_repo(repo_name)
			except GithubException:
				print "Repo '{}' not found".format(repo_name)

		return repo


	def create_update_mirror_repo(self, org_name, repo_name, src_url, pr_hook_url):

		repo = self.get_repo_object(org_name, repo_name)
		
		if repo is not None:
			print "WARNING: Repo '{}' already exists in the mirror github account".format(repo_name)
		else:
			repo = org.create_repo(repo_name)
			print "Repo '{}' created".format(repo_name)

		self.setup_basic_mirror_repo(repo, src_url, pr_hook_url)
		print "Basic mirror setup completed"

			
	def setup_basic_mirror_repo(self, repo_object, src_url, pr_hook_url):

		desc = "This is a mirror repo. Please fork from {}.".format(src_url)

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

		repo = self.get_repo_object(org_name, repo_name)

		if repo is not None:
			pr = repo.get_pull(pull_request_number)

			if pr.state != "closed":
				pr.create_issue_comment(reply)
				pr.edit(state="closed")
				print "Pull request with number {} has been closed".format(pull_request_number)
			else:
				print "Pull request with number {} is already closed".format(pull_request_number)


	def print_org_repos_size(self, org_name):

		organization = self.get_org_object(org_name)

		if organization is not None:
			repo_count = 0
			total_size = 0

			for repo in organization.get_repos():
				repo_count += 1
				total_size += repo.size
				print "{}({} KB)".format(repo.name, repo.size)

			print "Number of repos: \t{}\nTotal size (KB):\t{}".format(repo_count, total_size)


	def create_release(self, org_name, repo_name, tag_name, name, body, 
					   draft, prerelease, assets):

		repo = self.get_repo_object(org_name, repo_name)

		if repo is None:
			return

		# Delete the release to recreate it
		for release in repo.get_releases():
			if release.tag_name == tag_name:
				release.delete_release()
				
		release = repo.create_git_release(tag=tag_name, name=name, message=body, 
									 	  draft=draft, prerelease=prerelease)

		for asset in assets:
			self.create_asset(asset["name"], asset["label"], asset["content_type"],
						 asset["browser_download_url"], release.upload_url)


	def create_asset(self, name, label, content_type, download_url, upload_url):

		if label is None:
			upload_url = upload_url.replace("{?name,label}", "")+"?name={}"
			upload_url = upload_url.format(name)
		else:
			upload_url = upload_url.replace("{?name,label}", "")+"?name={}&label={}"
			upload_url = upload_url.format(name, quote(label))

		headers = {"Content-type": content_type,
				   "Authorization": "token {}".format(self.token)}

		data = urllib2.urlopen(download_url).read()

		res = requests.post(url=upload_url,
							data=data,
							headers=headers,
							verify=False)

