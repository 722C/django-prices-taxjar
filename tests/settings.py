import os

SECRET_KEY = 'irrelevant'

INSTALLED_APPS = ['django_prices_taxjar']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'database.sqlite'}}

TAXJAR_ACCESS_KEY = os.environ.get('TAXJAR_ACCESS_KEY', '')
