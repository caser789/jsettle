class ClearingOrderGid(object):

    def __init__(self):
        self._id = 0

    def get(self):
        res = self._id
        self._id += 1
        return res


clearing_order_gid = ClearingOrderGid()
