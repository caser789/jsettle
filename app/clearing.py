import time

from collections import namedtuple

from model import const
from model.clearing_reference_mapping import clearing_reference_mapping
from model.clearing_order import clearing_order
from model.clearing_order import Status


Order = namedtuple(
    'Order',
    [
        'merchant_id',
        'order_amount',
        'currency',
        'order_type',
        'order_id',
        'order_complete_time',
        'order_owner_level',
        'store_id',  # optional ?
        'payment_method',  # optional ?
    ],
)


def schedule(service_id, order):
    payout_order_id = _try_get_existing_payout_order_id(service_id, order)
    if payout_order_id is not None:
        return payout_order_id

    order_record = _persist_within_transaction(service_id, order)

    _start_clearing(order_record.clearing_order_id)


def _try_get_existing_payout_order_id(service_id, order):
    mapping = clearing_reference_mapping.get(service_id, order.order_type, order.order_id)
    if mapping is not None:
        return mapping.clearing_order_id


def _persist_within_transaction(service_id, order):
    clearing_entity_id = None
    if order.order_owner_level == const.OwnerLevel.STORE:
        clearing_entity_id = order.store_id
    elif order.order_owner_level == const.OwnerLevel.MERCHANT_HOST:
        clearing_entity_id = order.merchant_id

    now = int(time.time())

    order_record = clearing_order.insert(
        order.order_complete_time,
        service_id=service_id,
        store_id=order.store_id,
        merchant_id=order.merchant_id,
        order_type=order.order_type,
        order_reference_id=order.order_id,
        order_complete_time=order.order_complete_time,
        order_amount=order.order_amount,
        currency=order.currency,
        payment_method=order.payment_method,
        clearing_entity_type=order.order_owner_level,
        clearing_entity_id=clearing_entity_id,
        status=Status.INITIAL,
        create_time=now,
        update_time=now,
    )

    clearing_reference_mapping.insert(
        service_id,
        order.order_type,
        order.order_id,
        sharding_table_index=util.get_table_shard_index(order_record.clearing_order_id),
        clearing_order_id=order_record.clearing_order_id,
    )

    return order_record


def _start_clearing(clearing_order_id):
    clearing_order = clearing_order.get(clearing_order_id)
    if order_record is None:
        return

    if order_record.status <= Status.INITIAL:
        if not assert_clearing_able(clearing_order):
            return

        # query MSS for settlement cycle, settlement level
        # update clearing order

    if order_record.status <= Status.ACCOUNTED_PROCESSING:
        # with transaction
        #   a. update status to Status.ACCOUNTED_PROCESSING
        #   b. do the clearing
        #   c. calc fees
        #   d. update status to Status.ACCOUNTED_COMPLETE
        pass

    if order_record.status <= Status.CLEARING_COMPLETE:
        # calc planned_settle_time
        # with transaction
        #   a. update planned_settle_time, status to Status.CLEARING_COMPLETE
        #   b. create pending_settlement_order
        pass


def assert_clearing_able(clearing_order):
    # '', 0, None
    if not clearing_order.clearing_entity_id:
        return False

    # '', OwnerLevel.UNKNOWN, None
    if not clearing_order.clearing_entity_type:
        return False

    if clearing_order.status != Status.INITIAL:
        return False

    return True
