#!/bin/bash

source $(dirname $0)/envs.sh
echo $PYTHONPATH
if [ -z PROJECT ]; then
    echo "Variavel PROJECT nao configurada"
    exit 1;
fi

pip install -r $pwd/requirements.txt

if [ ! -d $pwd/src/$PROJECT ]; then
    django-admin.py startproject $PROJECT $src
fi

cd $pwd/src/
python manage.py createcachetable django_cache
