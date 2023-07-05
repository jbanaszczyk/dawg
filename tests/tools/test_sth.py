from unittest import TestCase

from src.tools.sth import get_sum


class Test(TestCase):
    def test_get_sum(self):
        self.assertEqual(get_sum(1, 2), 3)
