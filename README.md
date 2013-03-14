cheddar
=======

Cheddar is my personal Google Reader :)


Requirements
============

 * RabbitMQ Server (or any other Celery [supported broker](http://docs.celeryproject.org/en/latest/getting-started/brokers/index.html))
 * PostgreSQL (or MariaDB/MySQL, I suggest PostgreSQL)
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