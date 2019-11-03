#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_django-activitylog
------------

Tests for `django-activitylog` models module.
"""

from django.test import TestCase
from django.utils import timezone

from activitylog.models import ActivityLog


class ActivityLogModelTests(TestCase):

    def test_str(self):
        # str method formats dates and truncates long log messages to
        # 100 chars
        activitylog = ActivityLog.objects.create(
            log="This is a long log message with many many many many many "
                "many characters.  126 in total, in fact. It will be "
                "truncated to 100."
        )
        truncated_log = 'This is a long log message with many many many ' \
                        'many many many characters.  126 in total, in fact. ' \
                        'It'
        self.assertEqual(activitylog.log[:100], truncated_log)
        self.assertEqual(len(truncated_log), 100)

        self.assertEqual(
            str(activitylog),
            '{} - {}'.format(
                timezone.now().strftime('%Y-%m-%d %H:%M %Z'), truncated_log
            )
        )
