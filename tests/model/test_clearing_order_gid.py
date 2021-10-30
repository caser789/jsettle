import unittest

from model.clearing_order_gid import ClearingOrderGid


class TestClearingOrderGid(object):

    def test_get(self):
        p = ClearingOrderGid()
        a = p.get()
        b = p.get()
        c = p.get()
        assert a == 0
        assert b == 1
        assert c == 2
