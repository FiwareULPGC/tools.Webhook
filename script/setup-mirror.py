#! /usr/bin/env  python

import os
import shutil
from subprocess import call
import sys

import yaml

sys.path.append(os.path.dirname(__file__))
from utils.utils import *
from utils.githubmirrorutils import GithubMirrorUtils


def setup_mirror(repo_clone_url, mirror_remote_url, token_file, pr_hook_url):

    directory = os.path.dirname(os.path.abspath(__file__))

    with open(directory+"/conf.yaml", "r") as f:
        config = yaml.load(f)
        config["workspace"] = os.path.expanduser(config["workspace"])
        pr_hook_url = config["pr_hook_url"]

    mirror_user_repo_name = get_user_repo_from_github_url(mirror_remote_url)
    clone_user_repo_name = get_user_repo_from_github_url(repo_clone_url)
    repository_folder = "{}/{}_{}".format(config["workspace"],
                                          mirror_user_repo_name['user'],
                                          mirror_user_repo_name['repo'])

    g = GithubMirrorUtils(token_file)

    if not os.path.exists(repository_folder):

        g.create_update_mirror_repo(mirror_user_repo_name['user'],
                                    mirror_user_repo_name['repo'],
                                    repo_clone_url,
                                    pr_hook_url)

        os.makedirs(repository_folder)

        if not ("source_repo_urls" in config):
            config["source_repo_urls"] = {}

        config["source_repo_urls"][repo_clone_url] = {"mirror_remote_url":
                                                      mirror_remote_url}

        with open(directory+"/conf.yaml", "w") as f:
            yaml.dump(config, f, default_flow_style=False)

    call(["git", "clone", "--mirror", repo_clone_url, repository_folder])

    with cd(repository_folder):
        call(["git", "remote", "set-url", "--push", "origin",
              mirror_remote_url])

        call(["git", "fetch", "-p", "origin"])
        call(["git", "push", "--mirror"])

    g.recreate_releases(clone_user_repo_name['user'],
                        clone_user_repo_name['repo'],
                        mirror_user_repo_name['user'],
                        mirror_user_repo_name['repo'])


if __name__ == "__main__":

    if len(sys.argv) < 4:
        print "Three arguments arguments are needed."
        sys.exit(-1)

    elif len(sys.argv) > 4:
        print "Only 3 arguments are accepted."
        sys.exit(-2)

    repo_clone_url = sys.argv[1]
    mirror_remote_url = sys.argv[2]
    token_file = sys.argv[3]

    setup_mirror(repo_clone_url, mirror_remote_url, token_file, pr_hook_url)
