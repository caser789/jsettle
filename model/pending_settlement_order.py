import time
from collections import namedtuple
from enum import Enum

from model import util


Row = namedtuple(
    'Row',
    [
        'id',
        'service_id',

        'clearing_order_id',
        'clearing_wallet_id',  # wallet id of store/merchant/merchant host id
        'clearing_entity_id',
        'clearing_entity_type',
        'sharding_table_index',

        'planned_settlement_time',
        'settlement_cycle',
        'settlement_trx_type',  # 1-Non-invoice (payment/refund/adjustment/cashout) 2-Invoice(Disbursement)
        'settlement_target_id',  # store/merchant/merchant host id
        'settlement_target_type',

        'create_time',
        'update_time',
    ],
)


class PendingSettlementOrder(object):

    # KEY (planned_settlement_time, settlement_target_id, clearing_entity_id)

    def __init__(self):
        self.rows = []

    def insert(self, **kw):
        new_id = len(self.rows)
        create_time = update_time = int(time.time())

        new_row = dummy_row._replace(id=new_id, create_time=create_time, update_time=update_time, **kw)
        self.rows.append(new_row)
        return 1


dummy_row = Row(
    id=0,
    service_id=0,

    clearing_order_id=0,
    clearing_wallet_id=0,
    clearing_entity_id=0,
    clearing_entity_type=0,
    sharding_table_index=0,

    planned_settlement_time=0,
    settlement_cycle=0,
    settlement_trx_type=0,
    settlement_target_id=0,
    settlement_target_type=0,

    create_time=0,
    update_time=0,
)
