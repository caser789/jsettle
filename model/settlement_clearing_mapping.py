import time
from collections import namedtuple
from enum import Enum

from model import util


Row = namedtuple(
    'Row',
    [
        'id',
        'settlement_order_id',
        'clearing_table_index',
        'clearing_order_id',
        'create_time',
    ],
)


SHARD_NUMBER = 300

class SettlementClearingMapping(object):

    # UKEY (settlement_order_id, clearing_order_id)

    def __init__(self):
        self.shards = [[] for _ in range(SHARD_NUMBER)]

    def insert(self, settlement_order_id, clearing_order_id):
        shard_index = settlement_order_id % SHARD_NUMBER
        shard = self.shards[shard_index]

        shard.append(Row(
            id=len(shard),
            settlement_order_id=settlement_order_id,
            clearing_table_index=util.get_table_shard_index(clearing_order_id),
            clearing_order_id=clearing_order_id,
            create_time=int(time.time()),
        ))
        return 1


settlement_clearing_mapping = SettlementClearingMapping()
