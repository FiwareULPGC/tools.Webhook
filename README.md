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
```
## repos folder
* Inside this directory the service will clone the duplicated repositories to be updated.
## script folder
* The **update-mirror.py** script is in charge of making the actual update to the mirrored repository.
* The **setup-mirror.py** script is provided to allow the initialization of a mirror repository without using the web service.
* Both scripts use the information stored in **conf.yaml** file to correctly prepare and update the mirrored repository.

### conf.yaml data structure

An example **conf.yaml** configuration is the following:
```
workspace: "/home/<username>/mirrors/repos"
fiwareulpgcmirror/source-repo:
  repository_folder: "fiwareulpgcmirror_source-repo"
  repository_to_mirror: "git@github.com:fiwareulpgcmirror/source-repo.git"
  repository_mirror_remote: "git@github.com:fiwareulpgcmirror/mirrored-repo.git"
fiwareulpgcmirror/source-repo2:
  repository_folder: "fiwareulpgcmirror_source-repo2"
  repository_to_mirror: "git@github.com:fiwareulpgcmirror/source-repo2.git"
  repository_mirror_remote: "git@github.com:fiwareulpgcmirror/mirrored-repo2.git"
```

* The **workspace** key tells the script were to clone and keep the repositories for the update operations.
* The rest of the first level keys, correspond with the name of the repository to be mirrored. We must use the the format *<user>/<repository_name> here, which will be compared with the **full_name** field of the hook request.

Inside the repository name keys, we must specify three additional keys:

* **repository_folder**: This key tells the script how to name the folder in which the the project willl be cloned. This folder will be created directly inside inside the indicated **workspace**.
* **repository_to_mirror**: Here the remote repository URL must be placed. The user **fiwareulpgc** must have the required configuration to be able to make a git clone to this repository without asking for further permissions.
* **repository_mirror_remote**: Here the mirrored repository URL must be placed. The user **fiwareulpgc** must have the required configuration to be able to push to this repository without asking for further permissions.

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

 * **update-mirror.py** must be granted execution rights.

 * User **www-data** must have access to **fiwareulpgc** user without needing password. In order to make sure it can only passwordless execute the update script, we must add the following line to **/etc/sudoers**:

 ```
 www-data ALL=(ALL) NOPASSWD: /home/<username>/mirrors/script/update-mirror.py
 ```
 
 ***NOTE***: It is recommended to always edit *sudoers* file using the command `visudo`.