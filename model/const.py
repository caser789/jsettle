from enum import Enum


class PaymentServiceProvider(Enum):
    """ upstream service (payment service provider), 1 for acquiring, 2 for MWS
    """
    UNKNOWN = 0
    ACQUIRING = 1
    MERCHANT_WALLET_SERVICE = 2


class OrderType(Enum):
    UNKNOWN = 0
    PAYMENT = 1
    REFUND = 2
    ADJUSTMENT_ADD = 3
    ADJUSTMENT_DEDUCT = 4
    DISBURSEMENT = 5  # cash in
    CASH_OUT = 6


class OwnerLevel(Enum):
    UNKNOWN = 0
    STORE = 1
    MERCHANT = 2
    MERCHANT_HOST = 3


class SettlementCycle(Enum):
    REALTIME = 1
    DAILY = 2
    WEEKLY = 3
    BIWEEKLY = 4
    MONTHLY = 5


class SettlementTarget(Enum):
    MERCHANT_HOST = 1
    MERCHANT = 2
    STORE = 3
