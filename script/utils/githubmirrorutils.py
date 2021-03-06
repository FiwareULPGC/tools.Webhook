#! /usr/bin/env  python

"""Module for GitHub interactions.

The module makes use of the library PyGitHub to facilitate the management
of the GitHub API. In the cases were PyGitHub does not support the API, the 
functions make direct HTTP requests.

"""

import os
import re

import json
import urllib2
from utils import normalise_repo_name

from github import Github, GithubException
import requests
from requests.utils import quote


class GithubMirrorUtils():

    """This class implements the operations needed to manage FIWARE mirrors."""

    def __init__(self, tokenfile=None):
        """The class needs a file with the GitHub authorization token.

        The token will be used to authorize all the queries against
        the GitHub API.

        """

        with open(tokenfile, "r") as f:
            self.token = f.read().strip()

            if self.token is None or self.token == "":
                raise ValueError("File {} is empty".format(tokenfile))

    def print_user_login(self):
        """Display authorized user name."""
        g = Github(self.token)
        print g.get_user().login

    def get_org_object(self, org_name):
        """Retrieve an owned PyGitHub organization object from its name.

        This method only searches for the organizations which are editable by
        the authorized user.

        """
        g = Github(self.token)

        organization = None
        for org in g.get_user().get_orgs():
            if org_name == org.login:
                organization = org
                break

        if organization is None:
            print ("Token user is not inside the organization "
                   "'{}'").format(org_name)

        return organization

    def get_public_org_object(self, org_name):
        """Retrieve a public PyGitHub organization object from its name.

        This method searches over the public organizations hosted on GitHub.

        """
        g = Github(self.token)

        organization = g.get_organization(org_name)
        for org in g.get_user().get_orgs():
            if org_name == org.login:
                organization = org
                break

        if organization is None:
            print "Organization '{}' not found".format(org_name)

        return organization

    def get_repo_object(self, org_name, repo_name):
        """Retrieve an owned PyGitHub repository object.

        This method only searches for the repositories whose organizations are 
        editable by authorized user.

        """
        organization = self.get_org_object(org_name)

        repo = None
        if organization is not None:
            try:
                repo = organization.get_repo(repo_name)
            except GithubException:
                print "Repo '{}' not found".format(repo_name)

        return repo

    def get_public_repo_object(self, org_name, repo_name):
        """Retrieve a public PyGitHub repository object.

        This method searches over the public organizations hosted on GitHub.

        """
        organization = self.get_public_org_object(org_name)

        repo = None
        if organization is not None:
            try:
                repo = organization.get_repo(repo_name)
            except GithubException:
                print "Repo '{}' not found".format(repo_name)

        return repo

    def create_update_mirror_repo(self, org_name, repo_name, src_url,
                                  pr_hook_url):
        """Create a new mirror or update a mirror definition information.

        When the mirror already exists, this method will simply update
        the description of the mirror and add the deny PR hook.

        """
        repo = self.get_repo_object(org_name, repo_name)

        if repo is not None:
            print ("WARNING: Repo '{}' already exists in the mirror "
                   "github account").format(repo_name)
        else:
            organization = self.get_org_object(org_name)
            repo = organization.create_repo(repo_name)
            print "Repo '{}' created".format(repo_name)

        self.setup_basic_mirror_repo(repo, src_url, pr_hook_url)
        print "Basic mirror setup completed"

    def setup_basic_mirror_repo(self, repo_object, src_url, pr_hook_url):
        """Set the mirror description and its deny PR hook."""
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

    def close_pull_request(self, org_name, repo_name, pull_request_number,
                           src_url):
        """Close the requested GitHub PR on the target repository."""
        reply = ("This is a mirror repo and the pull request has been closed "
                 "automatically.\n"
                 "Please, submit your pull request to {}.").format(src_url)

        repo = self.get_repo_object(org_name, repo_name)

        if repo is not None:
            pr = repo.get_pull(pull_request_number)

            if pr.state != "closed":
                pr.create_issue_comment(reply)
                pr.edit(state="closed")
                print ("Pull request with number {} "
                       "has been closed").format(pull_request_number)
            else:
                print ("Pull request with number {} is already "
                       "closed").format(pull_request_number)

    def print_org_repos_size(self, org_name):
        """Display a list of repository names and their sizes."""
        organization = self.get_org_object(org_name)

        if organization is not None:
            repo_count = 0
            total_size = 0

            for repo in organization.get_repos():
                repo_count += 1
                total_size += repo.size
                print "{}({} KB)".format(repo.name, repo.size)

            print ("Number of repos: \t{}\n"
                   "Total size (KB):\t{}").format(repo_count, total_size)

    def create_release(self, org_name, repo_name, tag_name, name, body,
                       draft, prerelease, assets):
        """Replicate a GitHub release in the mirror repository."""
        repo = self.get_repo_object(org_name, repo_name)

        if repo is None:
            return

        # Delete the release to recreate it
        for release in repo.get_releases():
            if release.tag_name == tag_name:
                release.delete_release()

        release = repo.create_git_release(tag=tag_name, name=name,
                                          message=body, draft=draft,
                                          prerelease=prerelease)

        for asset in assets:
            self.create_asset(asset["name"], asset["label"],
                              asset["content_type"],
                              asset["browser_download_url"],
                              release.upload_url)

    def create_asset(self, name, label, content_type, download_url,
                     upload_url):
        """Create and upload a new asset for a mirror repository.

        The assets upload method is not supported by PyGitHub. This method
        downloads an asset from the original repository and makes a new asset
        upload in the mirrored repository by querying against the GitHub API
        directly.

        """
        if label is None:
            upload_url = upload_url.replace("{?name,label}", "") + "?name={}"
            upload_url = upload_url.format(name)
        else:
            upload_url = upload_url.replace("{?name,label}", "") +\
                "?name={}&label={}"
            upload_url = upload_url.format(name, quote(label))

        headers = {"Content-type": content_type,
                   "Authorization": "token {}".format(self.token)}

        data = urllib2.urlopen(download_url).read()

        res = requests.post(url=upload_url,
                            data=data,
                            headers=headers,
                            verify=False)

    def recreate_releases(self, source_org, source_repo, mirror_org,
                          mirror_repo):
        """Get the source repository releases and reupload them to the mirror.

        The retrieval of public repositories releases is not supported by
        PyGitHub. This method queries directly against the GitHub API to
        receive a descriptive list of releases to be recreated in the 
        corresponding mirror repository.

        """
        print "Recreating releases for repository {}/{}".format(mirror_org,
                                                                mirror_repo)

        page = 1
        headers = {"Authorization": "token {}".format(self.token)}
        next_page = True

        while next_page:
            url = ("https://api.github.com/repos"
                   "/{}/{}/releases?page={}").format(source_org, source_repo,
                                                     page)
            res = requests.get(url=url,
                               headers=headers,
                               verify=False)

            releases = json.loads(res.text)
            for release in releases:
                self.create_release(mirror_org, mirror_repo,
                                    release["tag_name"], release["name"],
                                    release["body"], release["draft"],
                                    release["prerelease"], release["assets"])

            page += 1
            if not ("link" in res.headers and
                    'rel="next"' in res.headers["link"]):
                next_page = False
