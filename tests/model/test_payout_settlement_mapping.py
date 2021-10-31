import unittest

from model import util
from model.payout_settlement_mapping import PayoutSettlementMapping


class TestPayoutSettlementMapping(object):

    def test_insert(self):
        m = PayoutSettlementMapping()

        payout_order_id1 = 1000010000000000101  # shard 1
        payout_order_id2 = 1000020000000000001  # shard 1
        payout_order_id3 = 1000010000000000002  # shard 202

        settlement_order_id = 1000010000000000004

        m.insert(payout_order_id1, settlement_order_id)
        m.insert(payout_order_id2, settlement_order_id)
        m.insert(payout_order_id3, settlement_order_id)

        assert len(m.shards[1]) == 2
        assert len(m.shards[202]) == 1

        assert m.shards[1][0].id == 0
        assert m.shards[1][0].payout_order_id == payout_order_id1
        assert m.shards[1][0].settlement_order_id == settlement_order_id

        assert m.shards[1][1].id == 1
        assert m.shards[1][1].payout_order_id == payout_order_id2
        assert m.shards[1][1].settlement_order_id == settlement_order_id

        assert m.shards[202][0].id == 0
        assert m.shards[202][0].payout_order_id == payout_order_id3
        assert m.shards[202][0].settlement_order_id == settlement_order_id
