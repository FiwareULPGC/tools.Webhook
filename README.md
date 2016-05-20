# Mirroring webhook

[![MIT license][license-image]][license-url]
[![Support][support-image]][support-url]

This repository contains a set of scripts to serve as a mirroring service for GitHub repositories.

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
* [Requests](https://pypi.python.org/pypi/requests/)

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

* PyGithub, used to access the GitHub API via Python code:

	```
	sudo pip install pygithub
	```

* Requests, used to access the GitHub API via Python code where PyGithub does not support the GitHub API:

	```
	sudo pip install requests
	```

### Deploying the code

The service is divided into PHP code (simply used as entry point and redirection) and Python code (the actual working code). The PHP code can be found inside the **web** folder and the Python code can be found inside the **script** folder.

#### Backend scripts

All the contents of the **script** folder should be placed in any desired location. In our examples, we have placed them inside **/home/<username>/mirrors/script** folder.

The following changes are needed for the service to work as expected:

* update-mirror.py and deny-pull-requests.py must be granted execution rights.

* User **www-data** must have access to the user without needing password. In order to make sure it can only passwordless execute the update script, we must add the following line to /etc/sudoers:

	```
	www-data ALL=(ALL) NOPASSWD: /home/<username>/mirrors/script/update-mirror.py, /home/<username>/mirrors/script/deny-pull-requests.py
	```

    NOTE: It is recommended to always edit sudoers file using the command visudo.

* The **workspace** key inside the **conf.yaml** file must be set to the desired folder to clone repositories.

* The user **<username>** must be able to `git clone` and `git push` to the remote repository. This means that the user must have correctly set up its SSH credentials to access GitHub.

#### Web service

All the contents of the **web** directory must be inside **/var/www/html/mirror**. This way the access URLs will be of the form `http://<server-ip>/mirror/<action-entry-point>`.

Inside **index.php** the following variables should be updated accordingly:

* **update_script**: Path to the script **update-mirror.py**.
* **deny_script**: Path to the script **deny-pull-requests.py**.
* **github_token_file**: Path to the textfile containing the GitHub API token

##### Apache configuration

Make sure that the **rewrite** module is activated:

* Execute `sudo a2enmod rewrite`.
* Add the following configuration to **/etc/apache2/sites-available/000-default.conf**:
```
<VirtualHost *:80>
        
        ServerAdmin webmaster@localhost
        DocumentRoot /var/www/html

        ErrorLog ${APACHE_LOG_DIR}/error.log
        CustomLog ${APACHE_LOG_DIR}/access.log combined

        <Directory /var/www/html>
                Options Indexes FollowSymLinks MultiViews
                AllowOverride all
                Order allow,deny
                allow from all
        </Directory>

</VirtualHost>
```

* Restart apache with `sudo service apache2 restart`.

## Configuration file

An example **conf.yaml** configuration is the following:
```
workspace: "/home/<username>/mirrors/repos"
source_repo_urls:
  https://github.com/telefonicaid/fiware-orion.git:
    mirror_remote_url: git@github.com:Fiware/context.Orion.git
```

* The **workspace** key tells the script were to clone and keep the repositories for the setup and update operations.
* The **source_repo_urls** key contains a dictionary of cloning URLS. 
* Every cloning URL is a key for a dictionary indicating the remote url for the mirrored repo. The remote url must be indicated under the key **mirror_remote_url**


## Setting up repositories

The **setup-mirror.py** script is provided to allow the initialization of a mirror repository without using the web service. It will also populate **conf.yaml** with the appropiate values and structure. It invoked using the folllowing parameters:

```
setup-mirror.py <github_source_clone_url> <github_mirror_remote_url> <path_to_token_file>
```

**Example:**
```
setup-mirror.py https://github.com/telefonicaid/fiware-orion.git git@github.com:Fiware/context.Orion.git utils/github-token
```

## Troubleshooting
If you have any feedback or issue please contact us at http://ask.fiware.org using the tag 'webhook'.

[license-image]: https://img.shields.io/badge/license-MIT-blue.svg
[license-url]: https://github.com/Fiware/tools.Webhook/blob/master/LICENSE

[support-image]: https://img.shields.io/badge/support-askbot-yellowgreen.svg
[support-url]: http://ask.fiware.org
