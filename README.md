NOTE:
=====

This project is no near of working, we just started to coding it, there is no
branches, nearly no tests or whatsoever, yet, you are free to join us :)

And please, help us to keep all the code and commits single-languaged, yet the
main commiters are Brazilian, we ask you to code in english only (except for the
translation files, of course). 

If you are good at writing tests, you are more than welcome to help us!


cheddar
=======

Cheddar is my personal Google Reader :)


Requirements
============

 * RabbitMQ Server (or any other Celery [supported broker](http://docs.celeryproject.org/en/latest/getting-started/brokers/index.html))
 * PostgreSQL (or MariaDB/MySQL, I suggest PostgreSQL) with UTF-8 encoding
 * virtualenv and pip
 * Shell knowledge
 

Instalation
===========

	$ git clone git@github.com:rafaelsdm/cheddar.git
	$ cd cheddar


Then a file named `localenv.sh` and add the following line:
	
	export DJANGO_SETTINGS_MODULE='cheddar.settings.myconf'


Then, run `./startup.sh`. By the first time you run it, your virtualenv will be 
created 

	
	$ ./startup.sh
	
By now you will receive an error that you must create your settings file,
some text like this:

    ...
    ...
    ImportError: Could not import settings 'monitor.settings.myconf' 
     (Is it on sys.path?): No module named monitor.settings.myconf
     

Then you need to create your settings file, it's just a simple [Django settings file](https://docs.djangoproject.com/en/1.5/ref/settings/),
but you can just copy example.py settings file and add whatever config you want
there.

    $ cp src/cheddar/settings/example.py src/cheddar/settings/myconf.py
     
If you decide to use another name for your settings file, feel free to add it to
.gitignore, we don't want to know your passwords neither your SECRET_KEY ;) 

The example.py file just imports default.py which has the default settings for a
common develop environment which considers sqlite database, rabbit-mq running 
locally with guest access enabled, database based caching and static/media root
poiting to PROJECT_ROOT (which is poiting to one dir up of src).

Now you are ready to go.


Using Python Shell
==================

If you ever want to run `python manage.py shell` or any other django command, 
just run before `source envs.py`, like this:

    $ source envs.py
    $ cd src
    $ python manage.py shell
    $ python manage.py celery worker -l ERROR
     

Note about SQLite
=================

Yet we avoid using database-specific features in the future we may need to use
database views, stored procedure or others, SQLite is a single-writer database
which, under Cheddar conditions, becomes a problem since we heavily 
multiprocessing with Celery, so you will experiment lots of "database is locked"
errors.

If you don't want to mess your desktop with databases running, start an instance
of a Linux running PostgreSQL and use it, or MySQL.
