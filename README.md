NOTE:
=====

If you are good at writing tests, you are more than welcome to help!


cheddar
=======

Cheddar is my personal Google Reader :)


Requirements
============

 * Shell knowledge
 * Docker (and Docker Compose)
 

Instalation
===========

	$ git clone git@github.com:rafaelsdm/cheddar.git
	$ cd cheddar
    $ docker-compose build
    $ docker-compose up -d
    $ docker-compose run --rm cheddar python manage.py migrate

Using Python Shell
==================

If you ever want to run `python manage.py shell` or any other django command, just prepend the
command with the `docker-compose` command, such as:

    $ docker-compose run --rm cheddar python manage.py shell
    $ docker-compose run --rm cheddar python manage.py whateva


Running the basics
==================

In order to access your Cheddar, you first need to create a superuser:

    $ docker-compose run --rm cheddar python manage.py createsuperuser

Now you can use your superuser and access http://localhost:8000/admin/ and
add your subscriptions or go to http://localhost:8000/feeds/my/sites/import/
and import your `subscriptions.xml` from Google Takeout.
