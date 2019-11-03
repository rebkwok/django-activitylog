=====
Usage
=====

To use django-activitylog in a project, add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'activitylog.apps.ActivitylogConfig',
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
