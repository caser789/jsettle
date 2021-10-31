import time
from collections import namedtuple
from enum import Enum

from model import util
from model.clearing_order_gid import clearing_order_gid


class PaymentServiceProvider(Enum):
    """ upstream service (payment service provider), 1 for acquiring, 2 for MWS
    """
    ACQUIRING = 1
    MWS = 2


class Status(Enum):
    INITIAL = 1
    ACCOUNTED_PROCESSING = 2
    ACCOUNTED_COMPLETE = 3
    CLEARING_COMPLETE = 4
    CLEARING_FAILED = 5


class OrderType(Enum):
    PAYMENT = 1
    REFUND = 2
    ADJUSTMENT_ADD = 3
    ADJUSTMENT_DEDUCT = 4
    DISBURSEMENT_OR_CASH_IN = 5
    CASH_OUT = 6


class SubOrderType(Enum):
    """only for refund currently
    """
    T0 = 1  # refund happens within settlement cycle of payment order
    T1 = 2  # refund happens after settlement cycle of payment order


class PaymentMethod(Enum):
    WALLET_BALANCE = 1
    CREDIT_DEBIT_CARD = 2
    SHOPEEPAYLATER = 3
    GIRO = 4


Row = namedtuple(
    'Row',
    [
        'id',
        'clearing_order_id',  # clearing order GID

        'status',
        'order_complete_time',
        'order_amount',
        'currency',
        'create_time',
        'update_time',

        # client info
        ## merchant info
        'merchant_id',
        'store_id',
        'merchant_host_id',

        'service_id',  # PaymentServiceProvider
        'order_type',
        'sub_order_type',
        'order_reference_id',  # ID of the client
        'payment_order_id',  # the original payment order id, only refund order will have this field
        'payment_method',

        # fee
        'fee_config',  # store MDR, VAT, WHT fee config, will be in JSON format
        'vat_fee',  # the fee amount that we record in our database
        'wht_fee',  # TODO what's this?
        'mdr_fee',  # TODO what's this?
        'cofunding_amount',
        'payable_amount',  # order_amount - all fees
        'settled_vat_fee',  # the fee amount that we really settled in our system
        'settled_wht_fee',
        'settled_mdr_fee',
        'settled_cofunding_amount',  # order_amount - all settled fees
        'settled_payable_amount',

        # clearing
        'clearing_trx_id',  # The transaction ID that returned by merchant wallet engine
        'clearing_wallet_id',  # The target wallet ID that we create transaction in MWE
        'clearing_entity_id',  # The entity id of target wallet ID, storeId/merchantId/merchant host ID
        'clearing_entity_type', # The entity type of target wallet ID, store/merchant/merchant host

        # settlement
        'settlement_order_id',  # the settlement order id for this clearing order
        'settlement_cycle',  # Daily/Weekly/Bi-Weekly/Monthly, Should get by store ID from MIS
        'planned_settlement_time',  # the expect settlement time for this clearing order
        'actual_settlement_time',  # the actual settlement time for this clearing order
        'settlement_target_type',  # The entity type of settlement target 1:store 2:merchant 3:merchant host
        'settlement_target_id',  # The entity id of settlement target
        'tax_invoice_status',
        'tax_invoice_id',  # for every clearing order has one tax record tax invoice table in TH/VN
        'error_code',  # the error code indicate failure reason of this clearing order
        'extra_data',  # store some info for report merchant_scope (on-us/off-us) external_merchant_id external_store_id
    ],
)

SHARD_NUMBER = 300

class ClearingOrder(object):

    # UKEY ctime
    # UKEY clearing_order_id
    # KEY `idx_clearing_wallet_id` (`clearing_wallet_id`,`settlement_target_id`,`settlement_target_type`

    def __init__(self):
        self.shards = [[] for _ in range(SHARD_NUMBER)]

    def insert(self, **kw):
        shard_index = kw['order_complete_time'] // 24 // 3600 % SHARD_NUMBER
        shard = self.shards[shard_index]

        clearing_order_id = kw.pop('clearing_order_id', self.create_new_clearing_order_id(shard_index))
        new_id = len(shard)

        new_row = dummy_row._replace(id=new_id, clearing_order_id=clearing_order_id, **kw)
        shard.append(new_row)
        return 1

    def get(self, clearing_order_id):
        shard_index = util.get_table_shard_index(clearing_order_id)
        shard = self.shards[shard_index]
        for r in shard:
            if r.clearing_order_id == clearing_order_id:
                return r

    def update(self, _id, clearing_order_id, **kw):
        update_time = kw.pop('update_time', int(time.time()))

        shard_index = util.get_table_shard_index(clearing_order_id)
        rows = self.shards[shard_index]
        row = rows[_id]

        new_row = row._replace(update_time=update_time, **kw)
        rows[_id] = new_row
        return 1

    def create_new_clearing_order_id(self, shard_index):
        gid = clearing_order_gid.get()
        return util.get_sharded_id(shard_index, gid)


dummy_row = Row(
    id=0,
    clearing_order_id=0,
    status=Status.INITIAL,
    order_complete_time=0,
    order_amount=0,
    currency='SGD',
    create_time=0,
    update_time=0,
    merchant_id=0,
    store_id=0,
    merchant_host_id=0,
    service_id=PaymentServiceProvider.ACQUIRING,
    order_type=OrderType.PAYMENT,
    sub_order_type=SubOrderType.T0,
    order_reference_id=0,
    payment_order_id=0,
    payment_method=PaymentMethod.WALLET_BALANCE,

    fee_config='',
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

    clearing_trx_id=0,
    clearing_wallet_id=0,
    clearing_entity_id=0,
    clearing_entity_type='',

    settlement_order_id=0,
    settlement_cycle='',
    planned_settlement_time=0,
    actual_settlement_time=0,
    settlement_target_type=1,
    settlement_target_id=0,
    tax_invoice_status='',
    tax_invoice_id=0,
    error_code=0,
    extra_data='',
)
