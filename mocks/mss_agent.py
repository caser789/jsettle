import random

from model import const


class MSSAgent(object):

    def __init__(self):
        pass

    def get_store_details(self, store_id):
        return {
            'settlement_cycle': random.choice([
                const.SettlementCycle.REALTIME,
                const.SettlementCycle.DAILY,
                const.SettlementCycle.WEEKLY,
                const.SettlementCycle.BIWEEKLY,
                const.SettlementCycle.MONTHLY,
            ]),
            'settlement_id': random.randint(1, 100),
            'settle_to': random.choice([
                const.SettlementTarget.MERCHANT_HOST,
                const.SettlementTarget.MERCHANT,
                const.SettlementTarget.STORE,
            ]),
        }

    def get_merchant_details(self, merchant_id):
        return {
            'settlement_cycle': random.choice([
                const.SettlementCycle.REALTIME,
                const.SettlementCycle.DAILY,
                const.SettlementCycle.WEEKLY,
                const.SettlementCycle.BIWEEKLY,
                const.SettlementCycle.MONTHLY,
            ]),
            'settlement_id': random.randint(1, 100),
            'settle_to': random.choice([
                const.SettlementTarget.MERCHANT_HOST,
                const.SettlementTarget.MERCHANT,
                const.SettlementTarget.STORE,
            ]),
        }


mss_agent = MSSAgent()
