#!/bin/bash
# Inicia o servico do gunicorn e encerra se for preciso

source $(dirname $0)/envs.sh

PIDFILE=$pwd/.gunicorn.pid
if [ -f $PIDFILE ];then
    echo -n "Encerrando gunicorn..."
    PID=`cat $PIDFILE`
    kill -2 $PID
    sleep 2
    echo "OK"
fi

cd $pwd/src/
python manage.py collectstatic --noinput

echo -n "Iniciando gunicorn..."
gunicorn_django -b 127.0.0.1:$PORT --workers=3 --max-request=100 -D -p $PIDFILE
cd -
echo "OK"

