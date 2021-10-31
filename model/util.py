order_id_version = 1
order_id_version_shift = 18
database_shard_index_shift = 16
table_shard_index_shift = 13


def get_sharded_id(table_shard_index, _id):
    return _get_sharded_id(0, table_shard_index, _id)


def _get_sharded_id(database_shard_index, table_shard_index, _id):
    assert order_id_version < 10**1
    assert database_shard_index < 10**2
    assert table_shard_index < 10**3
    assert _id <= 10**13

    return (
        order_id_version * 10**order_id_version_shift +
        database_shard_index * 10**database_shard_index_shift +
        table_shard_index * 10**table_shard_index_shift +
        _id
    )


def get_table_shard_index(_id):
    _id = _id % 10**database_shard_index_shift
    return _id // 10**table_shard_index_shift
