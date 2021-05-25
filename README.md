# Course Request Form

A site that manages the creation of SRS courses in Penn's Canvas instance. Built with [Django](https://www.djangoproject.com/).

For more information, see the [wiki](https://github.com/Mfhodges/CRF2/wiki).

Production instance: [http://reqform01.library.upenn.int/](http://reqform01.library.upenn.int/)
Development instance: [http://reqform01.library.upenn.int/](http://reqform-dev.library.upenn.int/)
Server configuration: [https://gitlab.library.upenn.edu/course-request/crf2_config](https://gitlab.library.upenn.edu/course-request/crf2_config)

## Development installation

1. Install Python 3.8.10 (recommend version management with [pyenv](https://github.com/pyenv/pyenv))
2. Create a [virtual environment](https://docs.python.org/3/tutorial/venv.html) via your preferred method
3. Install project dependencies: `pip install -r requirements.txt`
4. Install [Oracle Instant Client](https://www.oracle.com/database/technologies/instant-client/downloads.html) for your platform
5. Create a config file at "config/config.ini" (you will need to create the "config" directory) and add the appropriate values. Here is a sample config file:

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

## Commands

Project settings are stored in "crf2/settings.py". For development, set `DEBUG = True` (be sure to revert this before committing your code!)

Commands are run by invoking them through the "manage.py" file. To see all available commands, run `python manage.py`.

To run the application the first time:

1. `python manage.py migrate` (you may also need to run `python manage.py makemigrations` -- you will be prompted if so)
2. `python manage.py runserver`

To log in as an admin: [http://localhost:8000/admin/](http://localhost:8000/admin/)
To log in as a user: [http://localhost:8000/accounts/login/](http://localhost:8000/accounts/login/)

For testing in a project-specific interactive shell, use `python manage.py shell_plus`.
