import time
from collections import namedtuple
from enum import Enum

from model import util


Row = namedtuple(
    'Row',
    [
        'id',
        'service_id',
        'order_type',
        'order_reference_id',
        'sharding_table_index',
        'clearing_order_id',
    ],
)


SHARD_NUMBER = 300

class ClearingReferenceMapping(object):

    # UKEY (order_reference_id, order_type, service_id)

    def __init__(self):
        self.shards = [[] for _ in range(SHARD_NUMBER)]

    def insert(self, service_id, order_type, order_reference_id, **kw):
        shard_index = self._hash(service_id, order_type, order_reference_id)
        shard = self.shards[shard_index]

        new_id = len(shard)

        new_row = dummy_row._replace(
            id=new_id,
            service_id=service_id,
            order_type=order_type,
            order_reference_id=order_reference_id,
            **kw
        )
        shard.append(new_row)
        return 1

    def get(self, service_id, order_type, order_reference_id):
        shard_index = self._hash(service_id, order_type, order_reference_id)
        shard = self.shards[shard_index]
        for r in shard:
            if r.service_id == service_id and r.order_type == order_type and r.order_reference_id == order_reference_id:
                return r

    def _hash(self, service_id, order_type, order_reference_id):
        k = '{}{}{}'.format(service_id, order_type, order_reference_id)
        return abs(hash(k)) % SHARD_NUMBER


dummy_row = Row(
    id=0,
    service_id=0,
    order_type=0,
    order_reference_id=0,
    sharding_table_index=0,
    clearing_order_id=0,
)


clearing_reference_mapping = ClearingReferenceMapping()
