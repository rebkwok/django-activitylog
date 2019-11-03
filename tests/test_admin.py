#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_django-activitylog
------------

Tests for `django-activitylog` admin module.
"""

from datetime import datetime

from django.contrib.admin.sites import AdminSite
from django.test import TestCase
from django.utils import timezone

from activitylog import admin
from activitylog.models import ActivityLog


class ActivityLogAdminTests(TestCase):

    def test_timestamp_display(self):
        ActivityLog.objects.create(
            timestamp=datetime(
                2016, 9, 15, 13, 45, 10, 12455, tzinfo=timezone.utc
            ),
            log="Message"
        )

        activitylog_admin = admin.ActivityLogAdmin(ActivityLog, AdminSite())
        al_query = activitylog_admin.get_queryset(None)[0]
        self.assertEqual(
            activitylog_admin.timestamp_formatted(al_query),
            '15-Sep-2016 13:45:10 (UTC)'
        )
