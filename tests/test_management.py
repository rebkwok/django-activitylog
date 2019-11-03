#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_django-activitylog
------------

Tests for `django-activitylog` management module.
"""

import os
import sys
from io import StringIO
from unittest.mock import patch

from datetime import datetime, timedelta
from model_bakery import baker
from dateutil.relativedelta import relativedelta

from django.conf import settings
from django.contrib.admin.sites import AdminSite
from django.core import management
from django.test import override_settings, TestCase
from django.utils import timezone

from activitylog import admin
from activitylog.models import ActivityLog


class ActivityLogAdminTests(TestCase):

    def test_timestamp_display(self):
        activitylog = ActivityLog.objects.create(
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

@override_settings(ACTIVITYLOG_EMPTY_JOB_TEXT=["emptylog1", "emptylog2"])
class DeleteEmptyJobActivityLogsTests(TestCase):

    def setUp(self):

        # logs 10, 20, 60 days ago, one for each empty job text msg, one other
        for days in [10, 20, 60]:
            baker.make(
                ActivityLog, log='Non empty message',
                timestamp=timezone.now()-timedelta(days),
            )
            for msg in settings.ACTIVITYLOG_EMPTY_JOB_TEXT:
                baker.make(
                    ActivityLog, log=msg,
                    timestamp=timezone.now()-timedelta(days),
                )

        self.total_empty_msg_count = len(settings.ACTIVITYLOG_EMPTY_JOB_TEXT)
        self.total_setup_logs = (self.total_empty_msg_count * 3) + 3

        self.output = StringIO()
        self.saved_stdout = sys.stdout
        sys.stdout = self.output

    def tearDown(self):
        self.output.close()
        sys.stdout = self.saved_stdout

    def test_delete_all_empty_logs(self):
        self.assertEqual(ActivityLog.objects.count(), self.total_setup_logs)
        management.call_command('delete_empty_job_logs', 'now')
        # only the 3 non-empty logs remain
        self.assertEqual(ActivityLog.objects.count(), 3)

    def test_delete_all_empty_logs_dry_run(self):
        self.assertEqual(ActivityLog.objects.count(), self.total_setup_logs)
        management.call_command('delete_empty_job_logs', 'now', dry_run=True)
        # all logs still remain
        self.assertEqual(ActivityLog.objects.count(), self.total_setup_logs)

    def test_delete_before_date(self):
        self.assertEqual(ActivityLog.objects.count(), self.total_setup_logs)

        # now - 30 days: deletes only empty 60-day-ago logs
        before_date = (timezone.now() - timedelta(30)).strftime('%Y%m%d')
        management.call_command('delete_empty_job_logs', before_date)
        # empty messages for 60 days ago deleted
        self.assertEqual(
            ActivityLog.objects.count(),
            self.total_setup_logs - self.total_empty_msg_count
        )

        # now - 20 days: deletes only empty 60-day-ago logs
        before_date = (timezone.now() - timedelta(20)).strftime('%Y%m%d')
        management.call_command('delete_empty_job_logs', before_date)
        # empty messages for 60 days ago deleted; assuming now is > 00:00,
        # messages created at now - 20 days will not be deleted
        self.assertEqual(
            ActivityLog.objects.count(),
            self.total_setup_logs - self.total_empty_msg_count
        )

        # now - 19 days: deletes only 20 and 60-day-ago logs
        before_date = (timezone.now() - timedelta(19)).strftime('%Y%m%d')
        management.call_command('delete_empty_job_logs', before_date)
        self.assertEqual(
            ActivityLog.objects.count(),
            self.total_setup_logs - (self.total_empty_msg_count * 2)
        )

    def test_before_date_in_future(self):
        self.assertEqual(ActivityLog.objects.count(), self.total_setup_logs)
        before_date = (timezone.now() + timedelta(1)).strftime('%Y%m%d')
        management.call_command('delete_empty_job_logs', before_date)

        self.assertEqual(
            self.output.getvalue(),
            'Invalid date {}; before date must be in the past.\n'.format(
                before_date
            )
        )
        self.assertEqual(ActivityLog.objects.count(), self.total_setup_logs)

    def test_invalid_before_date(self):
        self.assertEqual(ActivityLog.objects.count(), self.total_setup_logs)

        management.call_command('delete_empty_job_logs', 'foo')
        self.assertEqual(ActivityLog.objects.count(), self.total_setup_logs)

        management.call_command('delete_empty_job_logs', '170901')
        self.assertEqual(ActivityLog.objects.count(), self.total_setup_logs)

        management.call_command('delete_empty_job_logs', '01092017')
        self.assertEqual(ActivityLog.objects.count(), self.total_setup_logs)

        self.assertEqual(
            self.output.getvalue(),
            'Invalid date; enter in format YYYYMMDD\n'
            'Invalid date; enter in format YYYYMMDD\n'
            'Invalid date; enter in format YYYYMMDD\n'
        )


class DeleteOldActivityLogsTests(TestCase):

    def setUp(self):

        # logs 13, 25, 37 months ago, one for each empty job text msg, one other
        self.mock_now = datetime(2019, 10, 1, tzinfo=timezone.utc)
        self.log_11monthsold = baker.make(ActivityLog, log='message', timestamp=self.mock_now-relativedelta(months=11))
        self.log_25monthsold = baker.make(ActivityLog, log='message', timestamp=self.mock_now-relativedelta(months=25))
        self.log_37monthsold = baker.make(ActivityLog, log='message', timestamp=self.mock_now-relativedelta(months=37))

    @patch('activitylog.management.commands.delete_old_activitylogs.subprocess.run')
    @patch('activitylog.management.commands.delete_old_activitylogs.timezone.now')
    def test_delete_default_old_logs_s3_backup(self, mock_now, mock_run):
        mock_now.return_value = self.mock_now
        self.assertEqual(ActivityLog.objects.count(), 3)
        # no age, defaults to 1 yr
        with override_settings(ACTIVITYLOG_BACKUP_TYPE="s3", ACTIVITYLOG_S3_BACKUP_PATH="s3://test"):
            management.call_command('delete_old_activitylogs')
        # 2 logs left - the one that's < 1 yrs old plus the new one to log this activity
        self.assertEquals(ActivityLog.objects.count(), 2)
        all_log_ids = ActivityLog.objects.values_list("id", flat=True)
        for log in [self.log_25monthsold, self.log_37monthsold]:
            self.assertNotIn(log.id, all_log_ids)
        self.assertIn(self.log_11monthsold.id, all_log_ids)

        self.assertEquals(mock_run.call_count, 1)
        cutoff = (self.mock_now-relativedelta(years=1)).strftime('%Y-%m-%d')
        base_filename = getattr(settings, "ACTIVITYLOG_BACKUP_ROOT_FILENAME", "activitylog_backup")
        filename = f"{base_filename}_{cutoff}_{self.mock_now.strftime('%Y%m%d%H%M%S')}.csv"
        mock_run.assert_called_once_with(
            ['aws', 's3', 'cp', filename, os.path.join("s3://test", filename)], check=True
        )

    @patch('activitylog.management.commands.delete_old_activitylogs.subprocess.run')
    @patch('activitylog.management.commands.delete_old_activitylogs.timezone.now')
    def test_delete_old_logs_with_args_s3_backup(self, mock_now, mock_run):
        mock_now.return_value = self.mock_now
        self.assertEqual(ActivityLog.objects.count(), 3)
        with override_settings(ACTIVITYLOG_BACKUP_TYPE="s3", ACTIVITYLOG_S3_BACKUP_PATH="s3://test"):
            management.call_command('delete_old_activitylogs', age=3)
        # 3 logs left - the 2 that are < 3 yrs old plus the new one to log this activity
        self.assertEquals(ActivityLog.objects.count(), 3)
        all_log_ids = ActivityLog.objects.values_list("id", flat=True)
        for log in [self.log_11monthsold, self.log_25monthsold]:
            self.assertIn(log.id, all_log_ids)
        self.assertNotIn(self.log_37monthsold.id, all_log_ids)

        self.assertEquals(mock_run.call_count, 1)
        cutoff = (self.mock_now-relativedelta(years=3)).strftime('%Y-%m-%d')
        base_filename = getattr(settings, "ACTIVITYLOG_BACKUP_ROOT_FILENAME", "activitylog_backup")
        filename = f"{base_filename}_{cutoff}_{self.mock_now.strftime('%Y%m%d%H%M%S')}.csv"
        mock_run.assert_called_once_with(
            ['aws', 's3', 'cp', filename, os.path.join("s3://test", filename)], check=True
        )

