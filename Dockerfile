FROM ubuntu:yakkety
MAINTAINER Brian Bustin
RUN apt-get update && apt-get install -y  libffi-dev python-dev python-pip sqlite3 libsqlite3-dev openssl libssl-dev && pip install --upgrade setuptools
RUN mkdir /opt/django-netjsonconfig
COPY . /opt/django-netjsonconfig/
RUN cd /opt/django-netjsonconfig/ && python setup.py develop && pip install -r requirements-test.txt && python tests/manage.py migrate && python tests/manage.py createsuperuser
EXPOSE 8000
ENTRYPOINT ["/opt/django-netjsonconfig/tests/manage.py", "runserver"]
