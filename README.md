## Required directory structure

The required directory structure for the scripts to work is the following:

```
| /home/<username>
| | mirrors
| | | repos
| | | script
| | | | conf.yaml
| | | | setup-mirror.py
| | | | update-mirror.py
| | | | update-def-mirrors.py
| | | | deny-pull-requests.py
| | | utils
| | | | githubmirrorutils.py
| | | | utils.py
```
## repos folder
* Inside this directory the service will clone the duplicated repositories to be updated.
## script folder
* The **update-mirror.py** script is in charge of making the actual update to the mirrored repository. It uses the data provided by **conf.yaml** to correctly prepare and update the mirrored repository.
* The **setup-mirror.py** script is provided to allow the initialization of a mirror repository without using the web service. It will also populate **conf.yaml** with the appropiate values and structure.
* The **update-def-mirros.py** script allows the user to create or update the definition, name and the pull request bot URL in a list of repositories.
* The **deny-pull-requests.py** script acts as the backend for the bot that automatically closes pull requests in mirrored repositories.
## utils folder
* This directory contains different utilities for managing the local repositories and the github account where to hold the mirrors.


### conf.yaml data structure

An example **conf.yaml** configuration is the following:
```
workspace: "/home/<username>/mirrors/repos"
source_repo_urls:
  https://github.com/fiwareulpgcmirror/source-repo.git:
    mirror_remote_url: git@github.com:fiwareulpgcmirror/mirrored-repo.git
  https://github.com/fiwareulpgcmirror/source-repo2.git:
    mirror_remote_url: git@github.com:fiwareulpgcmirror/mirrored-repo2.git
```

* The **workspace** key tells the script were to clone and keep the repositories for the update operations.
* The **source_repo_urls** key contains a dictionary of cloning URLS. 
* Every cloning URL is a key for a dictionary indicating the remote url for the mirrored repo. The remote url must be indicated under the key **mirror_remote_url**

## Web service

The web service components can be seen below:

```
| web
| | Slim-2.6.2
| | .htaccess
| | index.php
```
* **Slim** is the framework used to facilitate the usage of REST requests and responses. In the current state, no complex treatment of the hook requests is being made.
* Inside **.htaccess** file we can find the redirection rules required for the REST service.
* **index.php** file receives the notifications from Github and it is in charge of redirecting the body to the **update-mirror.py** script. This way, the repository to be updated can be determined.
* All the contents of the **web** directory must be inside **/var/www/html/mirror**.

## System configuration

The following changes are needed for the service to work as expected:

 * **update-mirror.py** and **deny-pull-requests.py** must be granted execution rights.

 * User **www-data** must have access to **<username>** user without needing password. In order to make sure it can only passwordless execute the update script, we must add the following line to **/etc/sudoers**:

 ```
 www-data ALL=(ALL) NOPASSWD: /home/<username>/mirrors/script/update-mirror.py
 ```
 
 ***NOTE***: It is recommended to always edit *sudoers* file using the command `visudo`.

## Setting up repositories

The **setup-mirror.py** script is invoked using the folllowing parameters:

```
setup-mirror.py <github_source_clone_url> <github_mirror_remote_url>
```

**Example:**
```
setup-mirror.py https://github.com/fiwareulpgcmirror/source-repo.git git@github.com:fiwareulpgcmirror/mirrored-repo.git
```