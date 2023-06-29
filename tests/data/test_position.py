import unittest
from packutils.data.position import Position


class PositionTest(unittest.TestCase):
    def test_position_attributes(self):
        # Create a Position object
        position = Position(10, 20, 30, 90)

        # Verify the attributes
        self.assertEqual(position.x, 10)
        self.assertEqual(position.y, 20)
        self.assertEqual(position.z, 30)
        self.assertEqual(position.rotation, 90)


if __name__ == '__main__':
    unittest.main()
