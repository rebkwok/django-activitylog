# -*- coding: utf-8 -*-
from datetime import datetime
from functools import reduce
import operator

from django.conf import settings
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.views.generic import ListView

from .forms import ActivityLogSearchForm
from .models import ActivityLog


class ActivityLogListView(ListView):

    model = ActivityLog
    template_name = 'activitylog/list.html'
    context_object_name = 'logs'
    paginate_by = 20

    def get_queryset(self):
        empty_job_text = getattr(settings, "ACTIVITYLOG_EMPTY_JOB_TEXT", [])
        queryset = ActivityLog.objects.exclude(log__in=empty_job_text).order_by('-timestamp')
        reset = self.request.GET.get('reset')
        search_submitted = self.request.GET.get('search_submitted')
        search_text = self.request.GET.get('search')
        search_date = self.request.GET.get('search_date')
        hide_empty_jobs = self.request.GET.get('hide_empty_jobs')
        if reset or (not (search_text or search_date) and hide_empty_jobs) or (not reset and not search_submitted):
            return queryset

        if not hide_empty_jobs:
            queryset = ActivityLog.objects.all().order_by('-timestamp')

        if search_date:
            try:
                search_date = datetime.strptime(search_date, '%d-%b-%Y')
                start_datetime = search_date.replace(tzinfo=timezone.utc)
                end_datetime = start_datetime.replace(hour=23, minute=59, second=59, microsecond=999999)
                queryset = queryset.filter(Q(timestamp__gte=start_datetime) & Q(timestamp__lte=end_datetime)).order_by('-timestamp')
            except ValueError:
                messages.error(
                    self.request, 'Invalid search date format.  Please select '
                    'from datepicker or enter using the format dd-Mmm-YYYY'
                )
                return queryset

        if search_text:
            search_words = search_text.split()
            search_qs = reduce(operator.and_, (Q(log__icontains=x) for x in search_words))
            queryset = queryset.filter(search_qs)

        return queryset

    def get_context_data(self):
        context = super().get_context_data()
        context['sidenav_selection'] = 'activitylog'

        search_submitted =  self.request.GET.get('search_submitted')
        hide_empty_cronjobs = self.request.GET.get('hide_empty_cronjobs') if search_submitted else 'on'

        search_text = self.request.GET.get('search', '')
        search_date = self.request.GET.get('search_date', None)
        reset = self.request.GET.get('reset')
        if reset:
            hide_empty_cronjobs = 'on'
            search_text = ''
            search_date = None
        form = ActivityLogSearchForm(
            initial={
                'search': search_text, 'search_date': search_date,
                'hide_empty_jobs': hide_empty_cronjobs
            })
        context['form'] = form

        return context
