FROM python:2.7
MAINTAINER rafaeljsg14@gmail.com

COPY requirements.txt /opt/cheddar/

WORKDIR /opt/cheddar/

RUN pip install -r requirements.txt
RUN bash -c "mkdir -p /var/cheddar/{media,static} && chown -R 1000:1000 /var/cheddar"

ENV PYTHONPATH=/opt/cheddar/
ENV DJANGO_SETTINGS_MODULE=cheddar.settings.docker

COPY . .

VOLUME /var/cheddar/media
VOLUME /var/cheddar/static
EXPOSE 8000
