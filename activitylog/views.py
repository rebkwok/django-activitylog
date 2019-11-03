# -*- coding: utf-8 -*-
from django.views.generic import ListView

from .models import ActivityLog


class ActivityLogListView(ListView):

    model = ActivityLog
