=============================
django-activitylog
=============================

.. image:: https://badge.fury.io/py/django_activitylog.svg
    :target: https://badge.fury.io/py/django_activitylog

.. image:: https://travis-ci.org/rebkwok/django_activitylog.svg?branch=master
    :target: https://travis-ci.org/rebkwok/django_activitylog

.. image:: https://codecov.io/gh/rebkwok/django_activitylog/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/rebkwok/django_activitylog

A simple django app for logging site activity

Documentation
-------------

The full documentation is at https://django_activitylog.readthedocs.io.

Quickstart
----------

Install django-activitylog::

    pip install django_activitylog

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...,
        "django.contrib.admin",
        "django.contrib.messages",
        "activitylog.apps.ActivitylogConfig",
        ...
    )

Add required middleware:

.. code-block:: python

    MIDDLEWARE = (
        ...,
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware"
            ...
    )

Add django-activitylog's URL patterns:

.. code-block:: python

    from activitylog import urls as activitylog_urls


    urlpatterns = [
        ...
        url(r'^', include(activitylog_urls)),
        ...
    ]

Add settings:
.. code-block:: python

    ACTIVITYLOG_TIMESTAMP_FORMAT = "%d-%b-%Y %H:%M:%S (%Z)"  # format for displaying log timestamps


Optional: if you want to use the delete_old_activitylogs management command to backup and delete old logs:

.. code-block:: python

    ACTIVITYLOG_EMPTY_JOB_TEXT = []  # default []
    ACTIVITYLOG_BACKUP_TYPE = ""  # options "s3" or "filesystem"; default "filesystem"
    ACTIVITYLOG_BACKUP_PATH = ""  # required if ACTIVITYLOG_BACKUP_TYPE == "filesystem"; path to back up logs
    ACTIVITYLOG_BACKUP_ROOT_FILENAME = ""  # base filename for backup; default "activitylog_backup"
    ACTIVITYLOG_S3_BACKUP_PATH = "s3://path/to/s3/bucket"  # required if ACTIVITYLOG_BACKUP_TYPE == "s3";

Features
--------

* TODO

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox

Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
