from model.payout_order import Status
from model.payout_order import payout_order


def update_invoice_order_status(invoice_order_id, status):
    update_order_status(invoice_order_id, status)


def update_payout_order_status(payout_order_id, status):
    update_order_status(payout_order_id, status)


def update_order_status(order_id, status):
    assert status in (Status.PAYOUT_COMPLETE, Status.PAYOUT_CLOSED)

    order = payout_order.get(order_id)
    assert order is not None
    assert order.status == Status.PAYOUT_PENDING_UPDATE

    order.update(order.id, order.payout_order_id, status=status)
