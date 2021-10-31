from model import util

class TestUtil(object):

    def test_shard_id_and_index(self):
        table_shard_index = 33
        _id = 1234567

        sid = util.get_sharded_id(table_shard_index, _id)
        assert sid == 1000330000001234567

        got = util.get_table_shard_index(sid)
        assert got == table_shard_index
