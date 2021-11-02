import time
from collections import namedtuple
from enum import Enum

from model import util
from model.settlement_order_gid import settlement_order_gid


class Status(Enum):
    INITIAL = 1
    SETTLEMENT_PROCESSING = 2
    SETTLEMENT_COMPLETE = 3
    SETTLEMENT_CLOSED = 4


Row = namedtuple(
    'Row',
    [
        'id',
        'settlement_order_id',
        'status',
        'order_amount',
        'currency',
        'actual_settlement_time',
        'create_time',
        'update_time',

        'store_id',
        'merchant_id',
        'merchant_host_id',

        'service_id',

        # fee
        'vat_fee',  # the fee amount that we record in our database
        'wht_fee',
        'mdr_fee',
        'cofunding_amount',
        'payable_amount',  # total amount - all fees
        'settled_vat_fee',  # the fee amount that we really settled in our system
        'settled_wht_fee',
        'settled_mdr_fee',
        'settled_cofunding_amount',
        'settled_payable_amount',  # total amount - all settled amount

        # clearing
        'clearing_wallet_id',  # the source wallet id to settle
        'clearing_entity_id',  # the source entityId to settle
        'clearing_entity_type',  # the source entity type  of source entityId

        # settlement
        'settlement_target_wallet_id',  # the target wallet id to settle
        'settlement_target_id',  # the store/merchant ID of target wallet
        'settlement_target_type',  # The entity type of settlement target store/merchant/merchant host
        'settlement_cycle',  # Daily/Weekly/Bi-Weekly/Monthly Should get by store ID from MIS
        'settlement_trx_type',  # 1-non invoice(payment/refund/adjustment/cash out) 2-invoice
        'settlement_sent_trx_id',  # The transaction ID of settlement sent that returned by merchant wallet engine

        # will be empty if this is self-settlement order
        'settlement_recv_trx_id',  # The transaction ID of settlement receive that returned by merchant wallet engine

        # payout
        'payout_order_id',
        'error_code',  # the error code indicate failure reason of this order
        'extra_data',
    ],
)

SHARD_NUMBER = 300

class SettlementOrder(object):

    # UKEY settlement_order_id
    # KEY create_time
    # KEY settlement_target_id

    def __init__(self):
        self.shards = [[] for _ in range(SHARD_NUMBER)]

    def insert(self, **kw):
        shard_index = kw['create_time'] // 24 // 3600 % SHARD_NUMBER
        shard = self.shards[shard_index]

        settlement_order_id = kw.pop('settlement_order_id', self.create_new_settlement_order_id(shard_index))
        new_id = len(shard)

        new_row = dummy_row._replace(id=new_id, settlement_order_id=settlement_order_id, **kw)
        shard.append(new_row)
        return 1

    def create_new_settlement_order_id(self, shard_index):
        gid = settlement_order_gid.get()
        return util.get_sharded_id(shard_index, gid)

    def get(self, settlement_order_id):
        shard_index = util.get_table_shard_index(settlement_order_id)
        shard = self.shards[shard_index]
        for r in shard:
            if r.settlement_order_id == settlement_order_id:
                return r

    def update(self, _id, settlement_order_id, **kw):
        update_time = kw.pop('update_time', int(time.time()))

        shard_index = util.get_table_shard_index(settlement_order_id)
        rows = self.shards[shard_index]
        row = rows[_id]

        new_row = row._replace(update_time=update_time, **kw)
        rows[_id] = new_row
        return 1


dummy_row = Row(
    id=0,
    settlement_order_id=0,
    status=0,
    order_amount=0,
    currency='',
    actual_settlement_time=0,
    create_time=0,
    update_time=0,

    store_id=0,
    merchant_id=0,
    merchant_host_id=0,
    service_id=0,

    vat_fee=0,
    wht_fee=0,
    mdr_fee=0,
    cofunding_amount=0,
    payable_amount=0,
    settled_vat_fee=0,
    settled_wht_fee=0,
    settled_mdr_fee=0,
    settled_cofunding_amount=0,
    settled_payable_amount=0,

    clearing_wallet_id=0,
    clearing_entity_id=0,
    clearing_entity_type='',

    settlement_target_wallet_id=0,
    settlement_target_id=0,
    settlement_target_type='',
    settlement_cycle='',
    settlement_trx_type='',
    settlement_sent_trx_id=0,
    settlement_recv_trx_id=0,

    payout_order_id=0,
    error_code=0,
    extra_data='',
)


settlement_order = SettlementOrder()
