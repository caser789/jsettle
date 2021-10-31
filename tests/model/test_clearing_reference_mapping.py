import unittest

from model import util
from model.clearing_reference_mapping import ClearingReferenceMapping


class TestClearingOrder(object):

    def test_insert_and_get(self):
        c = ClearingReferenceMapping()

        c.insert(1, 2, 3)
        a = c.get(1, 2, 3)

        assert a.id == 0
        assert a.service_id == 1
        assert a.order_type == 2
        assert a.order_reference_id == 3

        c.insert(2, 2, 3)
        a = c.get(2, 2, 3)

        assert a.id == 0
        assert a.service_id == 2
        assert a.order_type == 2
        assert a.order_reference_id == 3
