import unittest

from model import util
from model.cron_job_lock import CronJobLock


class TestCronJobLock(object):

    def test_insert(self):
        lock = CronJobLock()

        a = lock.acquire(1, 2)
        assert a is True

        b = lock.acquire(1, 2)
        assert b is False

        c = lock.release(1, 2)
        assert c is True

        d = lock.release(1, 2)
        assert d is False
