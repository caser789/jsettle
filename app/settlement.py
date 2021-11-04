import time
import json

from model import const
from model.clearing_order import clearing_order
from model.cron_job_lock import cron_job_lock
from model.pending_settlement_order import pending_settlement_order
from model.settlement_clearing_mapping import settlement_clearing_mapping
from model.settlement_order import Status
from model.settlement_order import TxnType
from model.settlement_order import settlement_order

from mocks.mss_agent import mss_agent
from mocks.mwe_agent import mwe_agent


def schedule_settlement(order_type):
    """
    order_type is invoice or non-invoice
    """
    offset = 0
    limit = 1000
    settlement_time = int(time.time())

    while True:
        order_indexes = pending_settlement_order.find_to_settle(
            order_type,
            settlement_time,
            offset,
            limit,
        )
        for order, indexes in order_indexes:
            execute_settlement(order, order_type, indexes)

        if len(orders) < limit:
            break

        offset += limit


def realtime_settlement(order, order_type, indexes):
    execute_settlement(order, order_type, indexes)


def retry_settlement(order_type):
    settlement_models = settlement_order.find_imcomplete_settlement_orders_to_retry_in_n_days(7, order_type)
    for model in settlement_models:
        lock = cron_job_lock.acquire(
            business_id='{}-{}'.format(model.settlement_target_id, model.settlement_target_type),
            business_type='schedule_settlement',
        )
        if not lock:
            continue

        if model.status == Status.INITIAL:
            info = mss_agent.get_entity_info(
                settlement_model.service_id,
                settlement_model.settlement_target_type,
                settlement_model.settlement_target_id,
            )
            settlement_order.update(
                settlement_model.id,
                settlement_model.settlement_order_id,
                settlement_target_wallet_id=info['wallet_account_id'],
            )

        if model.status <= Status.SETTLEMENT_PROCESSING:
            extra_data, settlement_sent_trx_id, settlement_recv_trx_id = create_settlement_transaction(settlement_model)
            settlement_order.update(
                settlement_model.id,
                settlement_model.settlement_order_id,
                status=Status.SETTLEMENT_COMPLETE,
                extra_data=extra_data,
                settlement_sent_trx_id=settlement_sent_trx_id,
                settlement_recv_trx_id=settlement_recv_trx_id,
            )


def create_settlement_clearing_mapping(settlement_model, clearing_indexes):
    order_types = [const.OrderType.ADJUSTMENT_ADD, const.OrderType.ADJUSTMENT_DEDUCT]
    amount = settlement_model.order_amount
    clearing_model = None

    for index in clearing_indexes:
        offset = 0
        limit = 1000
        while True:
            clearing_models = clearing_order.find_by_pending_settlement(index, settlement_model, offset, limit, order_types)
            for clearing_model in clearing_models:
                if clearing_model.order_type in [const.OrderType.ADJUSTMENT_DEDUCT, const.OrderType.REFUND]:
                    amount -= clearing_model.order_amount
                else:
                    amount += clearing_model.order_amount

                # update settlement order ID to clearing_order model
                clearing_models = clearing_order.update(
                    clearing_model.id,
                    clearing_model.clearing_order_id,
                    settlement_order_id=settlement_model.settlement_order_id,
                )

                # create settlement_clearing_mapping
                settlement_clearing_mapping.insert(
                    settlement_model.settlement_order_id,
                    clearing_model.clearing_order_id,
                )

                # delete pending settlement order
                pending_settlement_order.delete(clearing_model.clearing_order_id)

            if len(clearing_models) < limit:
                break

    return clearing_model


def create_settlement_transaction(settlement_model):
    extra_data = json.loads(settlement_model.extra_data)
    if settlement_model.settlement_trx_type == TxnType.NON_INVOICE:
        extra_data = {
            'fund_transaction_type': const.MWETrxType.POSITIVE or const.MWETrxType.NEGATIVE or const.MWETrxType.INSTANT,
            'settlement_sent_amount': 0,
            'settlement_recv_amount': 0,
            'fee_amount': 0,
            'fee_type': const.MWEFeeType.PAYMENT or const.MWEFeeType.REFUND,
        }
    elif settlement_model.settlement_trx_type == TxnType.INVOICE:
        extra_data = {
            'settlement_sent_amount': settlement_model.order_amount,
            'fund_transaction_type': (
                const.MWETrxType.INSTANT
                if settlement_model.clearing_wallet_id == settlement_model.settlement_target_wallet_id else
                const.MWETrxType.NEGATIVE
            ),
        }
    else:
        raise Exception('not support')

    settlement_sent_trx_id = 0
    settlement_recv_trx_id = 0
    if extra_data['fund_transaction_type'] == const.MWETrxType.INSTANT:
        transaction = mwe_agent.create_transaction(settlement_model, const.MWETrxType.INSTANT)
        settlement_sent_trx_id = transaction['transaction_id']
    elif extra_data['fund_transaction_type'] == const.MWETrxType.POSITIVE:
        transaction = mwe_agent.try_positive_sent_transaction(settlement_model, const.MWETrxType.POSITIVE)
        settlement_sent_trx_id = transaction['transaction_id']
        transaction = mwe_agent.create_positive_received_transaction(settlement_model, const.MWETrxType.POSITIVE)
        settlement_recv_trx_id = transaction['transaction_id']

        mwe_agent.confirm_positive_sent_transaction(settlement_model, const.MWETrxType.POSITIVE)
    else:
        # extra_data['fund_transaction_type'] == const.MWETrxType.NEGATIVE
        transaction = mwe_agent.try_negative_sent_transaction(settlement_model, const.MWETrxType.POSITIVE)
        settlement_sent_trx_id = transaction['transaction_id']
        transaction = mwe_agent.create_negative_received_transaction(settlement_model, const.MWETrxType.POSITIVE)
        settlement_recv_trx_id = transaction['transaction_id']

        mwe_agent.confirm_negative_sent_transaction(settlement_model, const.MWETrxType.POSITIVE)

    return extra_data, settlement_sent_trx_id, settlement_recv_trx_id


def execute_settlement(order, order_type, indexes):
    """
    order: pending_settlement_order
    """
    lock = cron_job_lock.acquire(
        business_id='{}-{}'.format(order.settlement_target_id, order.settlement_target_type),
        business_type='schedule_settlement',
    )
    if not lock:
        return

    # with transaction
    # 1. create settlement order
    t = int(time.time())
    settlement_model = settlement_order.insert(
        status=Status.INITIAL,
        service_id=order.service_id,
        clearing_entity_id=order.clearing_entity_id,
        clearing_entity_type=order.clearing_entity_type,
        settlement_trx_type=order_type,
        settlement_target_id=order.settlement_target_id,
        settlement_target_type=order.settlement_target_type,
        create_time=t,
        update_time=t,
    )
    clearing_model = create_settlement_clearing_mapping(settlement_model, indexes)
    settlement_order.update(
        settlement_model.id,
        settlement_model.settlement_order_id,
        store_id=clearing_model.store_id,
        merchant_id=clearing_model.merchant_id,
        merchant_host_id=clearing_model.merchant_host_id,
        currency=clearing_model.currency,
        clearing_wallet_id=clearing_model.clearing_wallet_id,
    )

    # 2. call MSS to get settlement wallet ID
    info = mss_agent.get_entity_info(
        settlement_model.service_id,
        settlement_model.settlement_target_type,
        settlement_model.settlement_target_id,
    )
    settlement_order.update(
        settlement_model.id,
        settlement_model.settlement_order_id,
        settlement_target_wallet_id=info['wallet_account_id'],
    )

    # 3. call MWE to create settlement transaction
    #    update settlement to complete
    extra_data, settlement_sent_trx_id, settlement_recv_trx_id = create_settlement_transaction(settlement_model)
    settlement_order.update(
        settlement_model.id,
        settlement_model.settlement_order_id,
        status=Status.SETTLEMENT_COMPLETE,
        extra_data=extra_data,
        settlement_sent_trx_id=settlement_sent_trx_id,
        settlement_recv_trx_id=settlement_recv_trx_id,
    )
