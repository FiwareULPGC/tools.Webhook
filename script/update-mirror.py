#! /usr/bin/env  python

import json
import os
import shutil
from subprocess import call
import sys

import yaml

sys.path.append(os.path.dirname(__file__))
from utils.utils import *


def update_mirror(payload_or_payload_file):
	try:
		body = json.loads(payload_or_payload_file)
	except ValueError as error:
		with open(payload_or_payload_file, "r") as f:
			body = json.load(f)

	directory = os.path.dirname(os.path.abspath(__file__))
	with open(directory+"/conf.yaml", "r") as f:
		config = yaml.load(f)
		config["workspace"] = os.path.expanduser(config["workspace"])

	repo_clone_url = body['repository']['clone_url']
	mirror_remote_url = config["source_repo_urls"][repo_clone_url]["mirror_remote_url"]

	user_repo_name = get_user_repo_from_github_url(mirror_remote_url)
	repository_folder = "{}/{}_{}".format(config["workspace"], user_repo_name['user'], user_repo_name['repo'])

	if not os.path.exists(repository_folder):
		os.makedirs(repository_folder)
		
		call(["git", "clone", "--mirror", repo_clone_url, repository_folder])

	with cd(repository_folder):
		call(["git", "remote", "set-url", "--push", "origin", mirror_remote_url])
		
		call(["git", "fetch", "-p", "origin"])
		call(["git", "push", "--mirror"])


if __name__ == "__main__":

	if len(sys.argv) < 2: 
		print "No arguments were passed."
		sys.exit(-1)

	elif len(sys.argv) > 2: 
		print "Only one argument is accepted."
		sys.exit(-2)

	payload_or_payload_file = sys.argv[1]

	update_mirror(payload_or_payload_file)