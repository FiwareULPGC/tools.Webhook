# Mirroring webhook

This repository contains a set of scripts to serve as a mirroring service for Github repositories.

## Operating System

The service has been developed and tested under Ubuntu 14.04 OS.

## Sytem dependencies

* [Python 2.7](https://www.python.org/)
* [Apache HTTP Server](https://httpd.apache.org/)
* [PHP5](http://php.net/downloads.php)
* [git](https://git-scm.com/)
* [pip](https://pypi.python.org/pypi/pip)

## Python dependencies

* [PyYAML](http://pyyaml.org/)
* [PyGithub](https://pypi.python.org/pypi/PyGithub)

## Installation and configuration guide

### Installing dependencies

Follow the commands below to install the system dependencies:

* Apache and PHP5:

	```
	sudo apt-get install apache2
	sudo apt-get install php5
	sudo apt-get install libapache2-mod-php5
	sudo service apache2 restart
	```

* Git command line tool:
	
	```
	sudo apt-get install git
	```

* Pip, python dependencies installer:
	
	```
	sudo apt-get install python-pip
	```

Now you are able to install the Python dependencies:

* PyYAML, used to manipulate configuration files in YAML format:

	```
	sudo pip install pyyaml
	```

* PyGithub, used to access the Github API via Python code:

	```
	sudo pip install pygithub
	```

### Deploying the code

The service is divided into PHP code (simply used as entry point and redirection) and Python code (the actual working code). The PHP code can be found inside the **web** folder and the Python code can be found inside the **script** folder.

#### Backend scripts

All the contents of the **script** folder should be placed in any desired location. In our examples, we have placed them inside **/home/<username>/mirrors/script** folder.

The following changes are needed for the service to work as expected:

* update-mirror.py and deny-pull-requests.py must be granted execution rights.

* User **www-data** must have access to the user without needing password. In order to make sure it can only passwordless execute the update script, we must add the following line to /etc/sudoers:

	```
	www-data ALL=(ALL) NOPASSWD: /home/<username>/mirrors/script/update-mirror.py
	```

    NOTE: It is recommended to always edit sudoers file using the command visudo.

* The **workspace** key inside the **conf.yaml** file must de set to the desired folder to clone repositories.

#### Web service

All the contents of the **web** directory must be inside **/var/www/html/mirror**. This way the access URLs will be of the form `http://<server-ip>/mirror/<action-entry-point>`.

Inside **index.php** the followint variables should be updated accordingly:

* **update_script**: Path to the script **update-mirror.py**.
* **deny_script**: Path to the script **deny-pull-requests.py**.
* **github_token_file**: Path to the textfile containing the Github API token

## Configuration file

An example **conf.yaml** configuration is the following:
```
workspace: "/home/<username>/mirrors/repos"
source_repo_urls:
  https://github.com/fiwareulpgcmirror/source-repo.git:
    mirror_remote_url: git@github.com:fiwareulpgcmirror/mirrored-repo.git
  https://github.com/fiwareulpgcmirror/source-repo2.git:
    mirror_remote_url: git@github.com:fiwareulpgcmirror/mirrored-repo2.git
```

* The **workspace** key tells the script were to clone and keep the repositories for the setup and update operations.
* The **source_repo_urls** key contains a dictionary of cloning URLS. 
* Every cloning URL is a key for a dictionary indicating the remote url for the mirrored repo. The remote url must be indicated under the key **mirror_remote_url**


## Setting up repositories

The **setup-mirror.py** script is provided to allow the initialization of a mirror repository without using the web service. It will also populate **conf.yaml** with the appropiate values and structure. It invoked using the folllowing parameters:

```
setup-mirror.py <github_source_clone_url> <github_mirror_remote_url>
```

**Example:**
```
setup-mirror.py https://github.com/fiwareulpgcmirror/source-repo.git git@github.com:fiwareulpgcmirror/mirrored-repo.git
```
