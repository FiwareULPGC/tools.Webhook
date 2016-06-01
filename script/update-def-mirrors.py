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
        pr_hook_url = config["pr_hook_url"]

    for repo_clone_url in config['source_repo_urls']:
        mirror_remote_url =\
            config['source_repo_urls'][repo_clone_url]["mirror_remote_url"]
        mirror_user_repo_name =\
            get_user_repo_from_github_url(mirror_remote_url)

        print mirror_user_repo_name

        g = GithubMirrorUtils(tokenfile=token_file)
        g.create_update_mirror_repo(mirror_user_repo_name['user'],
                                    mirror_user_repo_name['repo'],
                                    repo_clone_url,
                                    pr_hook_url)


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print "Only 1 argument is accepted."
        sys.exit(-1)

    update_def_mirrors(sys.argv[1])
