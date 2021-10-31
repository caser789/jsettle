import unittest

from model import util
from model.clearing_order import ClearingOrder
from model.clearing_order import Row
from model.clearing_order import SHARD_NUMBER


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

    def test_get(self):
        order_complete_time = 24*3600
        table_shard_index = order_complete_time // 24 // 3600 % SHARD_NUMBER
        _id = 1234567
        clearing_order_id = util.get_sharded_id(table_shard_index, _id)

        c = ClearingOrder()
        c.insert(order_complete_time=order_complete_time, clearing_order_id=clearing_order_id)

        r = c.get(clearing_order_id)
        assert r.clearing_order_id == clearing_order_id
