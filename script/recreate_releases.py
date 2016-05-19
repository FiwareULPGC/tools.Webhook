#! /usr/bin/env  python

import os
import shutil
from subprocess import call
import sys

import yaml

sys.path.append(os.path.dirname(__file__))
from utils.utils import *
from utils.githubmirrorutils import GithubMirrorUtils


def update_def_mirrors(token_file):

	directory = os.path.dirname(os.path.abspath(__file__))

	with open(directory+"/conf.yaml", "r") as f:
		config = yaml.load(f)
		config["workspace"] = os.path.expanduser(config["workspace"])

	for repo_clone_url in config['source_repo_urls']:
		mirror_remote_url = config['source_repo_urls'][repo_clone_url]["mirror_remote_url"]
		mirror_user_repo_name = get_user_repo_from_github_url(mirror_remote_url)
		clone_user_repo_name = get_user_repo_from_github_url(repo_clone_url)
		
		g = GithubMirrorUtils(tokenfile=token_file)

		g.recreate_releases(clone_user_repo_name['user'], clone_user_repo_name['repo'],
							mirror_user_repo_name['user'], mirror_user_repo_name['repo'])


if __name__ == "__main__":

	update_def_mirrors(sys.argv[1])

