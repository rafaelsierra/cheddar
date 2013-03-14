#!/bin/bash

source $(dirname $0)/envs.sh


if [ -z PROJECT ]; then
    echo "Variavel PROJECT nao configurada"
    exit 1;
fi

if [ ! -d $env ]; then
    echo 'ERROERROERROERROERROERROERROERROERROERROERROERROERROERROERROERROERROERROERROERRO'
    echo 'ERRO                                                                        ERRO'
    echo 'ERRO Não foi possivel iniciar o runserver, você já executou o ./startup.sh? ERRO'
    echo 'ERRO                                                                        ERRO'
    echo 'ERROERROERROERROERROERROERROERROERROERROERROERROERROERROERROERROERROERROERROERRO'
fi

cd $src
python manage.py syncdb --noinput
python manage.py migrate
python manage.py runserver 0.0.0.0:$PORT
cd -
