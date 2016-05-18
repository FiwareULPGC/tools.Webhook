# Contents description

* The **update-mirror.py** script is in charge of making the actual update to the mirrored repository. It uses the data provided by **conf.yaml** to correctly prepare and update the mirrored repository.
* The **setup-mirror.py** script is provided to allow the initialization of a mirror repository without using the web service. It will also populate **conf.yaml** with the appropiate values and structure.
* The **update-def-mirros.py** script allows the user to create or update the definition, name and the pull request bot URL in a list of repositories.
* The **deny-pull-requests.py** script acts as the backend for the bot that automatically closes pull requests in mirrored repositories.
* The **recreate-releases.py** script allows the user to delete and create every release in a list of repositories.


* The **utils** directory contains different utilities for managing the local repositories and the github account where to hold the mirrors.