import unittest

from model.settlement_order_gid import SettlementOrderGid


class TestSettlementOrderGid(object):

    def test_a(self):
        p = SettlementOrderGid()
        a = p.get()
        b = p.get()
        c = p.get()
        assert a == 0
        assert b == 1
        assert c == 2
