import time
from collections import namedtuple
from enum import Enum

from model import util


Row = namedtuple(
    'Row',
    [
        'id',
        'business_id',
        'business_type',
        'create_time',
        'update_time',
    ],
)

SHARD_NUMBER = 300

class CronJobLock(object):

    # UKEY (business_id, business_type)

    def __init__(self):
        self.rows = {}

    def acquire(self, business_id, business_type):
        key = (business_id, business_type)
        if key in self.rows:
            return False

        self.rows[key] = True
        return True

    def release(self, business_id, business_type):
        key = (business_id, business_type)
        if key not in self.rows:
            return False

        del self.rows[key]
        return True


cron_job_lock = CronJobLock()
