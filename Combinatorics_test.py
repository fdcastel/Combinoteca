import unittest

from Combinatorics import C, rank, partialMatches, allCombinations

class CombinatoricsTests(unittest.TestCase):

    def test_C(self):
        self.assertEqual(50063860, C(60, 6))
        self.assertEqual(1, C(6, 6))
        self.assertEqual(0, C(5, 6))

    def test_rank(self):
        self.assertEqual(1, rank([1, 2, 3, 4, 5, 6]))
        self.assertEqual(2, rank([1, 2, 3, 4, 5, 7]))
        self.assertEqual(3, rank([1, 2, 3, 4, 5, 8]))

        self.assertEqual(54, rank([1, 2, 3, 4, 5, 59]))
        self.assertEqual(55, rank([1, 2, 3, 4, 5, 60]))

        self.assertEqual(56, rank([1, 2, 3, 4, 6, 7]))
        self.assertEqual(57, rank([1, 2, 3, 4, 6, 8]))
        self.assertEqual(58, rank([1, 2, 3, 4, 6, 9]))

        self.assertEqual(5006387, rank([2, 3, 4, 5, 6, 7]))

        self.assertEqual(50063858, rank([54, 55, 57, 58, 59, 60]))
        self.assertEqual(50063859, rank([54, 56, 57, 58, 59, 60]))
        self.assertEqual(50063860, rank([55, 56, 57, 58, 59, 60]))
        
if __name__ == '__main__':
    unittest.main()
