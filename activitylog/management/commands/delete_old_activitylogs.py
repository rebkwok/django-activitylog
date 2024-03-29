import csv
import os
import subprocess

from dateutil.relativedelta import relativedelta

from django.conf import settings
from django.core import management
from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.encoding import smart_str

from ...models import ActivityLog


class Command(BaseCommand):

    help = "Delete old ActivityLogs"

    def add_arguments(self, parser):
        parser.add_argument(
            '--age',
            default=1,
            type=int,
            help='Age (in years) of logs to delete.  Defaults to 1 yr, i.e. will delete all logs older than 1 year old'
        )

    def handle(self, *args, **options):
        age = options.get('age')
        now = timezone.now()
        # set cutoff to beginning of this day <age> years ago
        cutoff = (now-relativedelta(years=age)).replace(hour=0, minute=0, second=0, microsecond=0)

        base_filename = getattr(settings, "ACTIVITYLOG_BACKUP_ROOT_FILENAME", "activitylog_backup")
        filename = f"{base_filename}_{cutoff.strftime('%Y-%m-%d')}_{now.strftime('%Y%m%d%H%M%S')}.csv"

        backup_type = getattr(settings, "ACTIVITYLOG_BACKUP_TYPE", "filesystem")
        if backup_type == "filesystem":
            backup_path =  settings.ACTIVITYLOG_BACKUP_PATH
            if not os.path.exists(backup_path):
                os.makedirs(backup_path)
        elif backup_type == "s3":
             s3_upload_path = os.path.join(settings.ACTIVITYLOG_S3_BACKUP_PATH, filename)
        else:
            raise ImproperlyConfigured("settings.BACKUP_TYPE is not valid")

        # Delete the empty logs first
        management.call_command('delete_empty_job_logs', cutoff.strftime('%Y%m%d'))

        old_logs = ActivityLog.objects.filter(timestamp__lt=cutoff)
        old_logs_count = old_logs.count()
        if old_logs_count > 0:
            with open(filename, "w") as outfile:
                wr = csv.writer(outfile)
                wr.writerow([
                    smart_str(u"Timestamp"),
                    smart_str(u"Log")
                ])
                for activitylog in old_logs:
                    wr.writerow([
                        smart_str(activitylog.timestamp.isoformat()),
                        smart_str(activitylog.log)
                    ])

            if backup_type == "filesystem":
                subprocess.run(["cp", filename, os.path.join(backup_path, filename)], check=True)
            elif backup_type == "s3":
                subprocess.run(["aws", "s3", "cp", filename, s3_upload_path], check=True)
            os.unlink(filename)

            old_logs.delete()
            message = f"{old_logs_count} activitylogs older than {cutoff.strftime('%Y-%m-%d')} backed up to s3 and deleted"
            self.stdout.write(message)
            ActivityLog.objects.create(log=message)
