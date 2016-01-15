#! /usr/bin/env  python

import os
import shutil
from subprocess import call
import sys

import yaml

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

if len(sys.argv) < 2: 
	print "No arguments were passed."
	sys.exit(-1)

elif len(sys.argv) > 2: 
	print "Only one argument is accepted."
	sys.exit(-2)

repo_name = sys.argv[1]

directory = os.path.dirname(os.path.abspath(__file__))

with open(directory+"/conf.yaml", "r") as f:
	config = yaml.load(f)
	config["workspace"] = os.path.expanduser(config["workspace"])
	
repository_folder = config["workspace"]+"/"+config[repo_name]["repository_folder"]

if os.path.exists(repository_folder):
	shutil.rmtree(repository_folder)

os.makedirs(repository_folder)

#print 'call(["git", "clone", "--mirror", {}, {}])'.format(config[repo_name]["repository_to_mirror"], repository_folder)
call(["git", "clone", "--mirror", config[repo_name]["repository_to_mirror"], repository_folder])

with cd(repository_folder):
	#print 'call(["git", "remote", "set-url", "--push", "origin", {}])'.format(config[repo_name]["repository_mirror_remote"])
	call(["git", "remote", "set-url", "--push", "origin", config[repo_name]["repository_mirror_remote"]])
	
	#print 'call(["git", "fetch", "-p", "origin"])'
	#print 'call(["git", "push", "--mirror"])'
	call(["git", "fetch", "-p", "origin"])
	call(["git", "push", "--mirror"])

