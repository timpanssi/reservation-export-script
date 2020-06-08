FROM python:3.5

ENV APP_NAME respa

RUN apt-get update
RUN apt-get install -y libgsl-dev libgdal20 gdal-data postgresql

COPY . /code
WORKDIR /code

RUN pip3 install setuptools==45
RUN pip3 install -r dev-requirements.txt