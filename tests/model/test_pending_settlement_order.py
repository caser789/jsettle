import unittest

from model import util
from model.pending_settlement_order import PendingSettlementOrder


class TestPendingSettlementOrder(object):

    def test_insert(self):
        p = PendingSettlementOrder()

        p.insert(clearing_order_id=0, clearing_wallet_id=1)
        p.insert(clearing_order_id=2, clearing_wallet_id=3)

        assert p.rows[0].id == 0
        assert p.rows[0].clearing_order_id == 0
        assert p.rows[0].clearing_wallet_id == 1

        assert p.rows[1].id == 1
        assert p.rows[1].clearing_order_id == 2
        assert p.rows[1].clearing_wallet_id == 3
