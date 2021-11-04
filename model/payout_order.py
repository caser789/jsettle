import time
from collections import namedtuple
from enum import Enum

from model import util
from model.payout_order_gid import payout_order_gid


class Status(Enum):
    UNKNOWN = 0
    INITIAL = 1
    PAYOUT_PROCESSING = 2
    PAYOUT_PENDING_UPDATE = 3
    PAYOUT_COMPLETE = 4
    PAYOUT_CLOSED = 5


Row = namedtuple(
    'Row',
    [
        'id',
        'payout_order_id',
        'payout_complete_time',
        'create_time',
        'update_time',
        'status',
        'payout_amount',  # sum(payable_amount)
        'settled_payout_amount',  # sum(settled_payable_amount)
        'currency',

        'payout_entity_type',
        'payout_entity_id',
        'payout_wallet_id',
        'service_id',

        'payout_option',  # No payout (manual withdrawal from FE App) Payout to Bank Acc Payout to shopeepay user wallet
        'payout_mode',  # Manual payout Auto payout
        'payout_trx_type',  # 1 = payout 2 = invoice
        'payout_trx_id',  # The payout/invoice transaction ID from MWS
        'payout_target_id',  # user wallet ID if payout to wallet/bank account ID if payout to bank

        # bank account
        'bank_id',
        'bank_name',
        'bank_account_name',
        'bank_account_number',

        'error_code',
        'extra_data',
    ],
)


SHARD_NUMBER = 300

class PayoutOrder(object):

    # UKEY payout_order_id
    # KEY create_time
    # KEY payout_trx_id

    def __init__(self):
        self.shards = [[] for _ in range(SHARD_NUMBER)]

    def insert(self, **kw):
        shard_index = kw['create_time'] // 24 // 3600 % SHARD_NUMBER
        shard = self.shards[shard_index]

        payout_order_id = kw.pop('payout_order_id', self.create_new_payout_order_id(shard_index))
        new_id = len(shard)

        new_row = dummy_row._replace(id=new_id, payout_order_id=payout_order_id, **kw)
        shard.append(new_row)
        return 1

    def create_new_payout_order_id(self, shard_index):
        gid = payout_order_gid.get()
        return util.get_sharded_id(shard_index, gid)

    def get(self, payout_order_id):
        shard_index = util.get_table_shard_index(payout_order_id)
        shard = self.shards[shard_index]
        for r in shard:
            if r.payout_order_id == payout_order_id:
                return r

    def update(self, _id, payout_order_id, **kw):
        update_time = kw.pop('update_time', int(time.time()))

        shard_index = util.get_table_shard_index(payout_order_id)
        rows = self.shards[shard_index]
        row = rows[_id]

        new_row = row._replace(update_time=update_time, **kw)
        rows[_id] = new_row
        return 1


dummy_row = Row(
    id=0,
    payout_order_id=0,
    payout_complete_time=0,
    create_time=0,
    update_time=0,
    status=0,
    payout_amount=0,
    settled_payout_amount=0,
    currency='',

    payout_entity_type=0,
    payout_entity_id=0,
    payout_wallet_id=0,
    service_id=0,

    payout_option=0,
    payout_mode=0,
    payout_trx_type=0,
    payout_trx_id=0,
    payout_target_id=0,

    bank_id=0,
    bank_name='',
    bank_account_name='',
    bank_account_number=0,

    error_code=0,
    extra_data='',
)


payout_order = PayoutOrder()
