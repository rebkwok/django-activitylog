# -*- coding: utf-8 -*-

from django.urls import include, path


urlpatterns = [
    path('', include('activitylog.urls', namespace='activitylog')),
]
