#! /usr/bin/env python
import os
from setuptools import setup

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.settings')

CLASSIFIERS = [
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
    'Topic :: Software Development :: Libraries :: Python Modules']

setup(
    name='django-prices-taxjar',
    author='7222C',
    description='taxjar.com support for django',
    license='BSD',
    version='0.0.1',
    url='https://github.com/722C/django-prices-taxjar',
    packages=[
        'django_prices_taxjar', 'django_prices_taxjar.migrations',
        'django_prices_taxjar.management',
        'django_prices_taxjar.management.commands'],
    include_package_data=True,
    classifiers=CLASSIFIERS,
    install_requires=[
        'Django>=1.11', 'prices>=1.0.0', 'requests', 'jsonfield'],
    platforms=['any'],
    zip_safe=False)
