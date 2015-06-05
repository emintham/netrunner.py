from unittest import TestCase


class TestHelper(TestCase):
    def assertLength(self, thing, expected_length):
        msg = 'Expected {} to have length {} but it has length {}'
        actual_length = len(thing)
        try:
            self.assertEqual(
                len(thing),
                expected_length,
                msg.format(thing, expected_length, actual_length)
            )
        except TypeError:
            raise TypeError('assertLength expects an object that has length!')

    def assertEmpty(self, thing):
        self.assertLength(thing, 0)
