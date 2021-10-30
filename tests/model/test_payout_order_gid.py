import unittest

from model.payout_order_gid import PayoutOrderGid


class TestPayoutOrderGid(object):

    def test_gid(self):
        p = PayoutOrderGid()
        a = p.get()
        b = p.get()
        c = p.get()
        assert a == 0
        assert b == 1
        assert c == 2
