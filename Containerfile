FROM python:3.5

ENV APP_NAME respa
ENV DJANGO_SETTINGS_MODULE=respa.development

RUN apt-get update
RUN apt-get install -y libgsl-dev libgdal20 gdal-data postgresql

COPY . /code
WORKDIR /code

RUN pip3 install setuptools==45

# Visual Studio Code dependencies
RUN apt-get install -y libatk1.0-dev libatk-bridge2.0-0 libdrm-dev libgtk-3-dev libgtk-3-dev libasound2-dev x11-xkb-utils