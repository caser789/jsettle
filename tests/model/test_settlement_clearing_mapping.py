import unittest

from model import util
from model.settlement_clearing_mapping import SettlementClearingMapping
from model.settlement_order import SettlementOrder
from model.clearing_order import ClearingOrder


class TestSettlementClearingMapping(object):

    def test_insert(self):
        m = SettlementClearingMapping()

        settlement_order_id1 = 1000010000000000101  # shard 1
        settlement_order_id2 = 1000020000000000001  # shard 1
        settlement_order_id3 = 1000010000000000002  # shard 202

        clearing_order_id = 1000010000000000004

        m.insert(settlement_order_id1, clearing_order_id)
        m.insert(settlement_order_id2, clearing_order_id)
        m.insert(settlement_order_id3, clearing_order_id)

        print(settlement_order_id1 % 300)
        print(settlement_order_id2 % 300)
        print(settlement_order_id3 % 300)

        assert len(m.shards[1]) == 2
        assert len(m.shards[202]) == 1

        assert m.shards[1][0].id == 0
        assert m.shards[1][0].settlement_order_id == settlement_order_id1
        assert m.shards[1][0].clearing_order_id == clearing_order_id

        assert m.shards[1][1].id == 1
        assert m.shards[1][1].settlement_order_id == settlement_order_id2
        assert m.shards[1][1].clearing_order_id == clearing_order_id

        assert m.shards[202][0].id == 0
        assert m.shards[202][0].settlement_order_id == settlement_order_id3
        assert m.shards[202][0].clearing_order_id == clearing_order_id
