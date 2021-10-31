import unittest

from model import util
from model.settlement_order import SettlementOrder
from model.settlement_order import Row
from model.settlement_order import SHARD_NUMBER


class TestSettlementOrder(object):

    def test_insert(self):
        c = SettlementOrder()

        c.insert(create_time=24*3600)
        assert len(c.shards[1]) == 1
        assert c.shards[1][0].id == 0
        assert c.shards[1][0].create_time == 24*3600
        assert c.shards[1][0].settlement_order_id == 1000010000000000000

        c.insert(create_time=24*3600)
        assert len(c.shards[1]) == 2
        assert c.shards[1][1].id == 1
        assert c.shards[1][1].create_time == 24*3600
        assert c.shards[1][1].settlement_order_id == 1000010000000000001

        c.insert(create_time=24*3600*2)
        assert len(c.shards[2]) == 1
        assert c.shards[2][0].id == 0
        assert c.shards[2][0].create_time == 24*3600*2
        assert c.shards[2][0].settlement_order_id == 1000020000000000002

        # test update
        settlement_order_id = 1000010000000000001
        r = c.get(settlement_order_id)
        c.update(r.id, r.settlement_order_id, update_time=123, order_amount=333)
        r = c.get(settlement_order_id)
        assert r.update_time == 123
        assert r.order_amount == 333

    def test_get(self):
        create_time = 24*3600
        table_shard_index = create_time // 24 // 3600 % SHARD_NUMBER
        _id = 1234567
        settlement_order_id = util.get_sharded_id(table_shard_index, _id)

        c = SettlementOrder()
        c.insert(create_time=create_time, settlement_order_id=settlement_order_id)

        r = c.get(settlement_order_id)
        assert r.settlement_order_id == settlement_order_id
