class MWEAgent(object):

    def create_transaction(self, settlement_model, fund_trn_type):
        req = {
            'service_id': settlement_order.service_id,
            'reference_id': settlement_order.settlement_order_id,
            'original_reference_id': settlement_order.settlement_order_id,
            'wallet_account_id': settlement_order.settlement_target_wallet_id,
            'fund_transaction_type': fund_trn_type,
            'amount': settlement_order.extra_data.settlement_trx_info.settlement_recv_amount,
            'fee_amount': settlement_order.extra_data.settlement_trx_info.fee_amount,
            'fund_movement_instructions': {
                'use_credit': True,
                'fee_type': settlement_order.extra_data.settlement_trx_info.fee_type,
            },
        }
        return {'transaction_id': 123}

    def try_positive_sent_transaction(self, settlement_model, fund_trn_type):
        return {'transaction_id': 123}

    def create_positive_received_transaction(self, settlement_model, fund_trn_type):
        return {'transaction_id': 123}

    def confirm_positive_sent_transaction(self, settlement_model, fund_trn_type):
        return {'transaction_id': 123}

    def try_negative_sent_transaction(self, settlement_model, fund_trn_type):
        return {'transaction_id': 123}

    def create_negative_received_transaction(self, settlement_model, fund_trn_type):
        return {'transaction_id': 123}

    def confirm_negative_sent_transaction(self, settlement_model, fund_trn_type):
        return {'transaction_id': 123}

mwe_agent = MWEAgent()
