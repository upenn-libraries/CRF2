# Course Request Form

Site that manages the creation of SRS courses in Penn's Canvas instance. Built with [Django](https://www.djangoproject.com/).

For more information, see the [wiki](https://github.com/Mfhodges/CRF2/wiki).

Production instance: [reqform01.library.upenn.int/](http://reqform01.library.upenn.int/)  
Development instance: [reqform-dev.library.upenn.int/](http://reqform-dev.library.upenn.int/)  
Server configuration: [https://gitlab.library.upenn.edu/course-request/crf2_config](https://gitlab.library.upenn.edu/course-request/crf2_config)

## Local Development

### Access Requirements

- [GlobalProtect VPN](https://www.isc.upenn.edu/how-to/university-vpn-getting-started-guide) (required to connect to the Data Warehouse)

### Installation

1. Install Python 3.6.5 (recommend version management with [pyenv](https://github.com/pyenv/pyenv))
2. Create a [virtual environment](https://docs.python.org/3/tutorial/venv.html) via your preferred method
3. Install project dependencies: `pip install -r requirements.txt`
4. Install [Oracle Instant Client](https://www.oracle.com/database/technologies/instant-client/downloads.html) for your platform
5. Create a "tnsnames.ora" file in your Oracle Instant Client's "network/admin" directory, using the following values:

```
WHSE.UPENN.EDU=
  (DESCRIPTION=
    (ADDRESS=
      (COMMUNITY=isc.penn)
      (PROTOCOL=TCP)
      (HOST=warehouse.isc.upenn.edu)
      (PORT=1521)
    )
    (CONNECT_DATA=
      (GLOBAL_NAME=whse)
      (SID=whse)
    )
  )
```

) 6. Create a config file at "config/config.ini" (you will need to create the "config" directory) and add the appropriate values. Here is a sample config file:

```ini
[django]
password = password
username = username
secret_key = secret-key
domain = http://127.0.0.1:8000/api/

[email]
password = password
emailhost = smtp.office365.com
emailhostuser = librarycanvas@pobox.upenn.edu
defaultfromemail = librarycrf@pobox.upenn.edu

[canvas]
test_env = https://upenn.test.instructure.com
test_key = secret-key
prod_env = https://canvas.upenn.edu
prod_key = secret-key

[opendata]
id = opendata-id
key = secret-key
domain = https://esb.isc-seo.upenn.edu/8091/open_data/
id_directory = opendata-id-directory
key_directory = secret-key

[users]
username = password

[datawarehouse]
user = LIBCANVAS
password = password
service = whse.upenn.edu
```

### Commands

Project settings are stored in "crf2/settings.py". For development, set `DEBUG = True` (be sure to revert this before committing your code!)

Commands are run by invoking them through the "manage.py" file. To see all available commands, run `python manage.py`.

To run the application the first time:

1. `python manage.py migrate` (you may also need to run `python manage.py makemigrations` -- you will be prompted if so)
2. `python manage.py runserver`

To log in as an admin: [http://localhost:8000/admin/](http://localhost:8000/admin/)  
To log in as a user: [http://localhost:8000/accounts/login/](http://localhost:8000/accounts/login/)

To test using your virtual environment's interactive shell, use `python manage.py shell_plus`.

## Server

### Access Requirements

- WireGuard VPN (must be set up through [Penn IT Help Desk](https://ithelp.library.upenn.edu/support/home)) 
- SSH access to the production and development domains
- Permissions to "switch user" to user "django"

### Commands

To login to the production and development instances:

1. `ssh reqform01.library.upenn.int` (production) or `ssh reqform-dev.library.upenn.int` (development)
2. `sudo su - django`

To pull changes from GitLab:

1. `cd /home/django/crf2`
2. `git pull`

To restart the app:

1. `cd /home/django/crf2/crf2`
2. `touch wsgi.py`

Working with the virtual environment:

- Activation: `source /home/django/venv/bin/activate`
- Deactivation: `exit`
