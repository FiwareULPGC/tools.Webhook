#! /usr/bin/env  python

import json
import os
import shutil
from subprocess import call
import sys

import yaml

sys.path.append(os.path.dirname(__file__))
from utils.githubmirrorutils import GithubMirrorUtils
from utils.utils import *


def deny_pull_requests(payload_or_payload_file, token_file):

    try:
        body = json.loads(payload_or_payload_file)
    except ValueError as error:
        with open(payload_or_payload_file, "r") as f:
            body = json.load(f)

    directory = os.path.dirname(os.path.abspath(__file__))
    with open(directory+"/conf.yaml", "r") as f:
        config = yaml.load(f)
        config["workspace"] = os.path.expanduser(config["workspace"])

    mirror_remote_url_from_body = body['repository']['ssh_url']
    mirror_user_repo_name = None

    for repo_clone_url in config['source_repo_urls']:
        mirror_remote_url =\
            config['source_repo_urls'][repo_clone_url]["mirror_remote_url"]

        if mirror_remote_url == mirror_remote_url_from_body:
            src_url = repo_clone_url
            mirror_user_repo_name =\
                get_user_repo_from_github_url(mirror_remote_url)

            print mirror_user_repo_name
            break

    if mirror_user_repo_name is None:
        print ("Entry {} not found in configuration "
               "file.").format(mirror_remote_url_from_body)
        return

    g = GithubMirrorUtils(tokenfile=token_file)

    org_name = mirror_user_repo_name['user']
    repo_name = mirror_user_repo_name['repo']
    pull_request_number = body['pull_request']['number']

    print "org_name:", org_name
    print "repo_name:", repo_name
    print "pull_request_number:", pull_request_number
    print "src_url:", src_url

    g.close_pull_request(org_name, repo_name, pull_request_number, src_url)


if __name__ == "__main__":

    if len(sys.argv) < 3:
        print "Less than two arguments were passed."
        sys.exit(-1)

    elif len(sys.argv) > 3:
        print "Only 2 arguments are accepted."
        sys.exit(-2)

    payload_or_payload_file = sys.argv[1]
    token_file = sys.argv[2]

    deny_pull_requests(payload_or_payload_file, token_file)
