import unittest

from model import util
from model.payout_order import PayoutOrder
from model.payout_order import Row
from model.payout_order import SHARD_NUMBER


class TestPayoutOrder(object):

    def test_insert_and_update(self):
        c = PayoutOrder()

        c.insert(create_time=24*3600)
        assert len(c.shards[1]) == 1
        assert c.shards[1][0].id == 0
        assert c.shards[1][0].create_time == 24*3600
        assert c.shards[1][0].payout_order_id == 1000010000000000000

        c.insert(create_time=24*3600)
        assert len(c.shards[1]) == 2
        assert c.shards[1][1].id == 1
        assert c.shards[1][1].create_time == 24*3600
        assert c.shards[1][1].payout_order_id == 1000010000000000001

        c.insert(create_time=24*3600*2)
        assert len(c.shards[2]) == 1
        assert c.shards[2][0].id == 0
        assert c.shards[2][0].create_time == 24*3600*2
        assert c.shards[2][0].payout_order_id == 1000020000000000002

        # test update
        payout_order_id = 1000010000000000001
        r = c.get(payout_order_id)
        c.update(r.id, r.payout_order_id, update_time=123, payout_amount=333)
        r = c.get(payout_order_id)
        assert r.update_time == 123
        assert r.payout_amount == 333

    def test_get(self):
        create_time = 24*3600
        table_shard_index = create_time // 24 // 3600 % SHARD_NUMBER
        _id = 1234567
        payout_order_id = util.get_sharded_id(table_shard_index, _id)

        c = PayoutOrder()
        c.insert(create_time=create_time, payout_order_id=payout_order_id)

        r = c.get(payout_order_id)
        assert r.payout_order_id == payout_order_id
