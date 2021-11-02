from mocks.mss_agent import mss_agent


class TestMSSAgent(object):

    def test_print(self):
        res = mss_agent.get_store_details(111)
        assert 'settlement_cycle' in res
        assert 'settlement_id' in res
        assert 'settle_to' in res
