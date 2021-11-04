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
        return new_row

    def delete(self, clearing_order_id):
        j = None
        for i, row in enumerate(selr.rows):
            if row.clearing_order_id == clearing_order_id:
                j = i
                break
        if j is not None:
            del self.rows[j]

    def find_to_settle(self, planned_settlement_time, settlement_trx_type, offset, limit):
        """
        return
            [
                (row, {sharding_index1, sharding_index2}),
                ...
            ]
        """
        if offset >= len(self.rows):
            return []

        store = {}
        for i in range(limit):
            j = i + offset
            if j >= len(self.rows):
                break

            row = self.rows[j]
            if row.planned_settlement_time >= planned_settlement_time:
                continue

            if row.settlement_trx_type != settlement_trx_type:
                continue

            key = (
                row.service_id,
                row.clearing_entity_id,
                row.clearing_entity_type,
                row.settlement_target_id,
                row.settlement_target_type,
                row.settlement_cycle,
            )
            if key in store:
                store[key][1].add(row.sharding_table_index)
                continue

            store[key] = [row, {row.sharding_table_index}]

        res = store.values()
        res.sort(key=lambda x: x[0].clearing_entity_id)
        return res


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


pending_settlement_order = PendingSettlementOrder()
