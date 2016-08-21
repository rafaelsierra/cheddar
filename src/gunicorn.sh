#!/bin/bash

# http://docs.gunicorn.org/en/stable/design.html#how-many-workers
NWORKERS=$(python -c "import multiprocessing;print((multiprocessing.cpu_count()*2)+1)")

python manage.py collectstatic --noinput

gunicorn -b 0.0.0.0:8000 \
    --workers=$NWORKERS \
    --timeout=30 \
    --keep-alive=3 \
    --max-requests=1000 \
    --max-requests-jitter=50 \
    --access-logfile=/dev/stdout \
    --error-logfile=/dev/stdout \
    --capture-output \
    cheddar.wsgi:application
