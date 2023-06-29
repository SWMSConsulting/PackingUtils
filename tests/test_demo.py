from packutils.test import test_constant
import unittest


class TestImports(unittest.TestCase):

    def test_upper(self):
        self.assertEqual(test_constant, 'FOO')


if __name__ == '__main__':
    unittest.main()
