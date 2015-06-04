from unittest import TestCase


class TestHelper(TestCase):
    def assertLength(self, thing, n):
        try:
            self.assertEqual(len(thing),
                             n,
                             'Expected {} to have length {}.'.format(thing, n))
        except TypeError:
            raise TypeError('assertEmpty expects an object that has length!')

    def assertEmpty(self, thing):
        self.assertLength(thing, 0)
