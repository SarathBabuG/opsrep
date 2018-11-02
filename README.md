# OpsRep

Ops Report

## Getting Started

### Prerequisites

```
python3
django
```

### Installation

```
apt-get install python3 python3-pip
pip3 install django
pip3 install djangorestframework
pip3 install django-url-filter
pip3 install django-apscheduler
pip3 install mysql-connector-python
pip3 install gunicorn
```

### Collect static files

```
python3 manage.py collectstatic
```

### Create DB file

```
python3 manage.py makemigrations
python3 manage.py showmigrations
python3 manage.py migrate

python3 manage.py makemigrations dashboards
python3 manage.py migrate dashboards

python3 manage.py makemigrations django_apscheduler
python3 manage.py migrate django_apscheduler
```

Create superuser to access DJango admin portal *http://127.0.0.1:8080/admin*

```
python3 manage.py createsuperuser
```
