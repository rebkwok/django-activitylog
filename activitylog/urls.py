# -*- coding: utf-8 -*-
from django.urls import path

from . import views


app_name = 'activitylog'

urlpatterns = [
    path('activitylog/', views.ActivityLogListView.as_view(), name='activitylog_list'),

]
