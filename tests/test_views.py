from datetime import datetime
from model_bakery import baker

from django.urls import reverse
from django.test import override_settings, TestCase
from django.utils import timezone

from activitylog.models import ActivityLog


@override_settings(ACTIVITYLOG_EMPTY_JOB_TEXT=['empty log', 'empty log 1'])
class ActivityLogListViewTests(TestCase):

    def setUp(self):
        super(ActivityLogListViewTests, self).setUp()
        self.url = reverse('activitylog:activitylog_list')

        baker.make(ActivityLog, log='empty log' )
        baker.make( ActivityLog, log='empty log 1')
        baker.make(ActivityLog, log='Test log message')
        baker.make(ActivityLog, log='Test log message1 One')
        baker.make(ActivityLog, log='Test log message2 Two')
        baker.make(
            ActivityLog,
            timestamp=datetime(2015, 1, 1, 16, 0, tzinfo=timezone.utc),
            log='Log with test date'
        )
        baker.make(
            ActivityLog,
            timestamp=datetime(2015, 1, 1, 4, 0, tzinfo=timezone.utc),
            log='Log with test date for search'
        )

    def test_empty_cron_job_logs_filtered_by_default(self):
        resp = self.client.get(self.url)
        self.assertEqual(len(resp.context_data['logs']), 5)

    def test_filter_out_empty_cron_job_logs(self):
        resp = self.client.get(self.url, data={'hide_empty_jobs': True})
        self.assertEqual(len(resp.context_data['logs']), 5)

    def test_search_text(self):
        resp = self.client.get(
            self.url,  data={'search_submitted': 'Search', 'search': 'message1'}
        )
        self.assertEqual(len(resp.context_data['logs']), 1)

        resp = self.client.get(
            self.url,  data={'search_submitted': 'Search', 'search': 'message'}
        )
        self.assertEqual(len(resp.context_data['logs']), 3)

    def test_search_is_case_insensitive(self):
        resp = self.client.get(
            self.url,  data={'search_submitted': 'Search', 'search': 'Message'}
        )
        self.assertEqual(len(resp.context_data['logs']), 3)

    def test_search_date(self):
        resp = self.client.get(
            self.url,  data={'search_submitted': 'Search', 'search_date': '01-Jan-2015'}
        )
        self.assertEqual(len(resp.context_data['logs']), 2)

    def test_invalid_search_date_format(self):
        """
        invalid search date returns all results and a message
        """
        resp = self.client.get(
            self.url,  data={'search_submitted': 'Search', 'search_date': '01-34-2015'}
        )
        self.assertEqual(len(resp.context_data['logs']), 7)

    def test_search_date_and_text(self):
        resp = self.client.get(
            self.url,  data={'search_submitted': 'Search', 'search_date': '01-Jan-2015', 'search': 'test date for search'}
        )
        self.assertEqual(len(resp.context_data['logs']), 1)

    def test_search_multiple_terms(self):
        """
        Search with multiple terms returns only logs that contain all terms
        """
        resp = self.client.get(
            self.url,  data={'search_submitted': 'Search', 'search': 'Message'}
        )
        self.assertEqual(len(resp.context_data['logs']), 3)

        resp = self.client.get(
            self.url,  data={'search_submitted': 'Search', 'search': 'Message One'}
        )
        self.assertEqual(len(resp.context_data['logs']), 1)

        resp = self.client.get(
            self.url,  data={'search_submitted': 'Search', 'search': 'test one'}
        )
        self.assertEqual(len(resp.context_data['logs']), 1)

    def test_reset(self):
        """
        Test that reset button resets the search text and date and excludes
        empty cron job messages
        """
        resp = self.client.get(
            self.url,  data={'search_submitted': 'Search', 'search_date': '01-Jan-2015', 'search': 'test date for search'}
        )
        self.assertEqual(len(resp.context_data['logs']), 1)

        resp = self.client.get(
            self.url,
            data={
                'search_submitted': 'Search',
                'search_date': '01-Jan-2015',
                'search': 'test date for search',
                'reset': 'Reset'
            }
        )
        self.assertEqual(len(resp.context_data['logs']), 5)
