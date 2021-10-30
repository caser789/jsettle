import unittest

from model.clearing_order import ClearingOrder
from model.clearing_order import Row


class TestClearingOrder(object):

    def test_insert(self):
        c = ClearingOrder()

        c.insert(order_complete_time=24*3600)
        assert len(c.shards[1]) == 1
        assert c.shards[1][0].id == 0
        assert c.shards[1][0].order_complete_time == 24*3600

        c.insert(order_complete_time=24*3600)
        assert len(c.shards[1]) == 2
        assert c.shards[1][1].id == 1
        assert c.shards[1][1].order_complete_time == 24*3600

        c.insert(order_complete_time=24*3600*2)
        assert len(c.shards[2]) == 1
        assert c.shards[2][0].id == 0
        assert c.shards[2][0].order_complete_time == 24*3600*2
