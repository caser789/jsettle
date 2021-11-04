import time

from collections import namedtuple

from model import util
from model import const
from model.clearing_reference_mapping import clearing_reference_mapping
from model.clearing_order import clearing_order
from model.clearing_order import Status
from model.settlement_order import TxnType
from model.pending_settlement_order import pending_settlement_order

from mocks.mss_agent import mss_agent


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
    payout_order_id = try_get_existing_payout_order_id(service_id, order)
    if payout_order_id is not None:
        return payout_order_id

    order_record = persist_within_transaction(service_id, order)

    start_clearing(order_record.clearing_order_id)


def retry():
    orders = clearing_order.find_imcomplete_orders_in_recent_n_days(7)

    for order in orders:
        start_clearing(order.clearing_order_id)


def try_get_existing_payout_order_id(service_id, order):
    mapping = clearing_reference_mapping.get(service_id, order.order_type, order.order_id)
    if mapping is not None:
        return mapping.clearing_order_id


def persist_within_transaction(service_id, order):
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


def start_clearing(clearing_order_id):
    model = clearing_order.get(clearing_order_id)
    if model is None:
        return

    if model.status <= Status.INITIAL:
        if not assert_clearing_able(model):
            return

        # query MSS for settlement cycle, settlement level
        # update clearing order
        if model.clearing_entity_type == const.OwnerLevel.STORE:
            model = update_clearing_order_with_mss_store_details(model)
        elif clearing_order.clearing_entity_type == const.OwnerLevel.MERCHANT:
            model = update_clearing_order_with_mss_merchant_details(model)

        if clearing_order.settlement_target_type  == const.OwnerLevel.MERCHANT:
            details = mss_agent.get_merchant_details(clearing_order.clearing_entity_id)
            if details['settle_to'] == const.SettlementTarget.MERCHANT_HOST:
                model = clearing_order.update(
                    model.id,
                    model.clearing_order_id,
                    settlement_target_type=details['settle_to'],
                    settlement_target_id=details['settlement_id'],
                )

    if model.status <= Status.ACCOUNTED_PROCESSING:
        # with transaction
        model = clearing_order.update(model.id, model.clearing_order_id, status=Status.ACCOUNTED_PROCESSING)
        # TODO do the clearing, calc fees
        model = clearing_order.update(model.id, model.clearing_order_id, status=Status.ACCOUNTED_COMPLETE)

    if model.status <= Status.CLEARING_COMPLETE:
        # with transaction
        planned_settle_time = get_planned_settle_time(model)
        model = clearing_order.update(
            model.id,
            model.clearing_order_id,
            planned_settlement_time=planned_settle_time,
            status=Status.CLEARING_COMPLETE,
        )

        t = int(time.time())
        settlement_trx_type = (
            TxnType.INVOICE if model.order_type == const.OrderType.DISBURSEMENT else TxnType.NON_INVOICE
        )
        pending_settlement_order.insert(
            service_id=model.service_id,
            clearing_order_id=model.clearing_order_id,
            clearing_entity_id=model.clearing_entity_id,
            clearing_entity_type=model.clearing_entity_type,
            sharding_table_index=util.get_table_shard_index(model.clearing_order_id),
            planned_settlement_time=planned_settle_time,
            settlement_cycle=model.settlement_cycle,
            settlement_trx_type=settlement_trx_type,
            settlement_target_type=model.settlement_target_type,
            settlement_target_id=model.settlement_target_id,
            create_time=t,
            update_time=t,
        )


def assert_clearing_able(model):
    # '', 0, None
    if not model.clearing_entity_id:
        return False

    # '', OwnerLevel.UNKNOWN, None
    if not model.clearing_entity_type:
        return False

    if model.status != Status.INITIAL:
        return False

    return True


def update_clearing_order_with_mss_store_details(model):
    details = mss_agent.get_store_details(model.clearing_entity_id)
    return _update_clearing_order_with_mss_details(model, details)


def update_clearing_order_with_mss_merchant_details(model):
    details = mss_agent.get_merchant_details(model.clearing_entity_id)
    return _update_clearing_order_with_mss_details(model, details)


def _update_clearing_order_with_mss_details(model, details):
    assert details['settlement_cycle'] in (const.SettlementCycle.REALTIME, const.SettlementCycle.DAILY)
    assert details['settle_to'] in (const.SettlementTarget.MERCHANT_HOST, const.SettlementTarget.STORE)

    return clearing_order.update(
        model.id,
        model.clearing_order_id,
        settlement_cycle=details['settlement_cycle'],
        settlement_target_type=details['settle_to'],
        settlement_target_id=details['settlement_id'],
    )


def get_planned_settle_time(model):
    current = int(time.time())
    order_complete_time = model.order_complete_time

    if model.settlement_cycle == const.SettlementCycle.REALTIME:
        return current - 1

    if model.settlement_cycle == const.SettlementCycle.DAILY:
        complete_next_day = order_complete_time + 24 * 3600
        if complete_next_day > current:
            return

        if settlement_order.find_by_clearing_order_current_time(model, current):
            return complete_next_day - 1

        return current - 1
