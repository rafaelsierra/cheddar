#!/bin/bash


export PROJECT='cheddar'
export PORT=16001
export pwd=$(cd $(dirname $0); pwd)

echo "Working dir: $pwd"
export env=~/envs/$PROJECT

echo "Environment dir: $env"
export src=$pwd/src
export PYTHONPATH=$PYTHONPATH:$src

if [ -f 'localenv.sh' ]; then
	source localenv.sh
else
	if [ -z "$DJANGO_SETTINGS_MODULE" ]; then
		echo "You need to set your \$DJANGO_SETTINGS_MODULE"
		echo "This can be done by export'ing or putting it into localenv.sh'"
		exit 1
	fi
fi



if [ ! -d $env ]; then
    virtualenv $env
fi
source $env/bin/activate
