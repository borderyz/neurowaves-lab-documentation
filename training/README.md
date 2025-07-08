Installing moodle and hp5 via docker
====================================
- Clone
- git clone --branch MOODLE_500_STABLE --depth 1 https://github.com/moodle/moodle.git moodle
- Run `scripts`
git submodule add -b MOODLE_500_STABLE https://github.com/moodle/moodle.git training/moodle
git commit -m "Add Moodle submodule in training/moodle"
git push


Database host	db	This must be the service name of the MariaDB container, not localhost. Inside the Moodle container localhost would point back to itself.
Database name	moodle	Matches MARIADB_DATABASE: moodle.
Database user	moodle	Matches MARIADB_USER: moodle.
Database password	moodlepass	Matches MARIADB_PASSWORD: moodlepass.
Tables prefix	mdl_ (default)	Leave as-is unless you need multiple Moodles in one DB.
Database port	3306 (or leave blank)	3306 is MariaDB’s default and Docker’s internal networking uses it automatically.
Unix socket	(leave blank)	Only used for same-host socket connections, not needed here.

- Access localhost or server and go through the moodle installation
- Download h5p plugin
- Activate h5p plugin by copying the plugin file to the docker container training-moodle-1, then bash upgrade using php admin/cli