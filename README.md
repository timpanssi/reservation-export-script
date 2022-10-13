
[![Stories in Ready](https://badge.waffle.io/City-of-Helsinki/respa.png?label=ready&title=Ready)](https://waffle.io/City-of-Helsinki/respa)
[![Build Status](https://api.travis-ci.org/City-of-Helsinki/respa.svg?branch=master)](https://travis-ci.org/City-of-Helsinki/respa)
[![codecov](https://codecov.io/gh/City-of-Helsinki/respa/branch/master/graph/badge.svg)](https://codecov.io/gh/City-of-Helsinki/respa)

respa – Resource reservation and management service
===================
Respa is a backend service for reserving and managing resources (e.g. meeting rooms, equipment, personnel). The open two-way REST API is interoperable with the [6Aika Resource reservation API specification](https://github.com/6aika/api-resurssienvaraus) created by the six largest cities in Finland. You can explore the API at [api.hel.fi](https://api.hel.fi/respa/v1/) and view the API documentation at [dev.hel.fi](https://dev.hel.fi/apis/respa/).

User interfaces for Respa developed by the City of Helsinki are [Varaamo](https://github.com/City-of-Helsinki/varaamo) and [Huvaja](https://github.com/City-of-Helsinki/huvaja), and the now-defunct [Stadin Tilapankki](https://github.com/City-of-Helsinki/tilapankki). The City of Hämeenlinna has developed a [Berth Reservation UI](https://github.com/CityOfHameenlinna/hmlvaraus-frontend) and [backend](https://github.com/CityOfHameenlinna/hmlvaraus-backend) on top of Respa.

Editing data can be done by using a simple UI based on Django admin.

Used by
------------

- [City of Helsinki](https://api.hel.fi/respa/v1/) - for [Varaamo UI](https://varaamo.hel.fi/) & [Huvaja UI](https://huonevaraus.hel.fi/)
- [City of Espoo](https://api.hel.fi/respa/v1/) - for [Varaamo UI](https://varaamo.espoo.fi/)
- [City of Vantaa](https://api.hel.fi/respa/v1/) - for [Varaamo UI](https://varaamo.vantaa.fi/)
- [City of Oulu](https://varaamo-api.ouka.fi/v1/) - for [Varaamo UI](https://varaamo.ouka.fi/)
- [City of Mikkeli](https://mikkeli-respa.metatavu.io/v1/) - for [Varaamo UI](https://varaamo.mikkeli.fi/)
- [City of Tampere](https://respa.tampere.fi/v1/) - for [Varaamo UI](https://varaamo.tampere.fi/)
- City of Hämeenlinna - for [Berth Reservation UI](https://varaukset.hameenlinna.fi/)

FAQ
------------

### Why is it called Respa?
Short for "RESurssiPAlvelu" i.e. Resource Service.

Setup development environment for Visual Studio Code Remote Container
---------------------------------------------------------------------

Install Remote Containers support in Visual Studio Code with these instructions:

* https://code.visualstudio.com/docs/remote/remote-overview
* https://code.visualstudio.com/docs/remote/containers

After that this should be easy, if all that magic works:

* Open the project folder in Visual Studio Code
* It asks to reopen the folder in remote container
* Accept
* Wait a while for it to automatically build the environment for you

In the debug panel you can run following with debugger enabled:

* Django runserver in hot reload mode
* Django shell
* Django migrations
* Generate new Django migrations for all Django apps

Here's some extra commands you may need:

* Install hstore extension (inside container) `echo "create extension hstore;" | python3 manage.py dbshell`
* Import database dump (outside container) `cat <name_of_the_sanitized_respa_dump>.sql | docker exec -i respa-db psql -U respa -d respa`

Setup development environment for Visual Studio Code with Podman + Toolbox
--------------------------------------------------------------------------

* Build image tailored for Toolbox: `podman build . -f Containerfile -t varaukset.hameenlinna.fi/env/respa:latest`.
* Create a toolbox container of the image: `toolbox create --image varaukset.hameenlinna.fi/env/respa:latest hameenlinna_respa`.
* Launch vscode installed on your host in the toolbox container: `toolbox run --container hameenlinna_respa /var/run/host/bin/code`.
* Create and activate virtual environment: `python -m venv .venv; source .venv/bin/activate`.
* Install dependencies: `pip install -r requirements.txt`.
* Start database service: `podman-compose start postgresql`.
* Install hstore extension: `echo "create extension hstore;" | python3 manage.py dbshell`
* Import database dump: `cat <name_of_the_sanitized_respa_dump>.sql | python3 manage.py dbshell`

Creating sanitized database dump
--------------------------------

This project uses Django Sanitized Dump for database sanitation.  Issue
the following management command on the server to create a sanitized
database dump:

    ./manage.py create_sanitized_dump > sanitized_db.sql

Contributing
------------

Your contributions are always welcome! If you want to report a bug or see a new feature feel free to create a new [Issue](https://github.com/City-of-Helsinki/respa/issues/new) or discuss it with us on [Gitter](https://gitter.im/City-of-Helsinki/heldev). Alternatively, you can create a pull request (base master branch). Your PR will be reviewed by the project tech lead.

License
------------

Usage is provided under the [MIT License](https://github.com/City-of-Helsinki/respa/blob/master/LICENSE).