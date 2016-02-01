#! /usr/bin/env  python

from lxml import html
import os
import re


class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


def get_user_repo_from_github_url(url):

	regex = ('(?:https://github.com/(?P<user1>.*)/(?P<repo1>.*).git)|'
		 '(?:git://github.com/(?P<user2>.*)/(?P<repo2>.*).git)|'
		 '(?:git@github.com:(?P<user3>.*)/(?P<repo3>.*).git)')

	github_pattern = re.compile(regex)

	url = url.strip(' \t\n\r')

	match_result = github_pattern.match(url)

	if match_result:
		result = match_result.groupdict()

		user = result['user1'] or  result['user2'] or result['user3']
		repo = result['repo1'] or  result['repo2'] or result['repo3']

		if user and repo:
			return {'user':user, 'repo':repo}
		else:
			raise ValueError("Error found with URL parsing")
	else:
		raise ValueError('The URL {} has invalid Github URL format.'.format(url))


def filter_fiware_prefix(name):

	regex = r'(?i)(fiware-?|fi-ware-?)'
	fiware_prefix_pattern = re.compile(regex)

	filtered_name = re.sub(fiware_prefix_pattern, '', name)

	return filtered_name


def capitalise_after_chapter(name):

	pos = name.find('.')

	name_list = list(name)

	name_list[pos+1] = name_list[pos+1].upper()

	return "".join(name_list)


def normalise_repo_name(repo_name):

	return capitalise_after_chapter(filter_fiware_prefix(repo_name))


def parse_clone_mirror_list(filepath, github_org):

	from pprint import pprint

	with open(filepath, "r") as f:
		tree = html.fromstring(f.read())

		chapters_repos = tree.xpath('//*[self::h2 or self::tr]')


		chapter = None
		clone_mirror_list = []
		for chapter_repo in chapters_repos:
			title = chapter_repo.xpath('span/text()')

			if title: #H2
				title = str(title[0]).strip(' ')
				chapter = title.split(' ')[0].lower()

			else: #TR
				title = chapter_repo.xpath('td/text()')

				if title:
					if title[0] == 'Github Repository\n':
						urls = chapter_repo.xpath('td/a/@href')
						
						for url in urls:
							if url.endswith('/'):
								url = url[0:-1]

							if len(url.split('/')) < 5:
								print "No repo in {}".format(url)
								continue

							repo_name = url.split('/')[4]
							source_url = url + '.git'
							if chapter == 'data':
								chapter == 'context'
							repo_name = normalise_repo_name(chapter+'.'+repo_name)
							remote_url = 'git@github.com:{}/{}.git'.format(github_org, 
										  repo_name)

							clone_mirror_list.append([source_url, remote_url]) 

		return clone_mirror_list


