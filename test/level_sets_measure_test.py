import itertools
import unittest

import numpy as np

from image_measures import measure_of_chaos, _level_sets, _default_measure


class MeasureOfChaosTest(unittest.TestCase):
    def test_measure_of_chaos_ValueError(self):
        valid_ims = (np.ones((3, 3)),)
        invalid_nlevelss = (0, -3)
        test_cases = itertools.product(valid_ims, invalid_nlevelss)
        for args in test_cases:
            self.assertRaises(ValueError, measure_of_chaos, *args)

    def test_measure_of_chaos_does_not_overwrite(self):
        im_before = np.linspace(0, 1, 100).reshape((10, 10))
        im_after = np.copy(im_before)
        measure_of_chaos(im_after, 10, overwrite=False)
        np.testing.assert_array_equal(im_before, im_after)

    def test__level_sets_ValueError(self):
        self.assertRaises(ValueError, _level_sets, np.arange(5), 0)

    def test__level_sets(self):
        test_cases = _make_level_sets_cases()
        for args, expected in test_cases:
            actual = _level_sets(*args)
            np.testing.assert_array_equal(actual, expected)

    def test__measure_ValueError(self):
        invalid_num_objs = ([], [-1], [2, -1], [2, -4, -1], [1, 2, 3, -1, 1, 2], [-0.001, 20])
        valid_num_objs = (range(5, 0, -1),)
        invalid_sum_notnulls = (-2.7, -1, 0,)
        valid_sum_notnulls = (15,)
        invalid_combinations = itertools.chain(itertools.product(invalid_num_objs, valid_sum_notnulls),
                                               itertools.product(valid_num_objs, invalid_sum_notnulls),
                                               itertools.product(invalid_num_objs, invalid_sum_notnulls))
        for num_objs, sum_notnull in invalid_combinations:
            self.assertRaises(ValueError, _default_measure, num_objs, sum_notnull)
        for num_objs, sum_notnull in itertools.product(valid_num_objs, valid_sum_notnulls):
            _default_measure(num_objs, sum_notnull)

    def test__measure_trivial(self):
        test_cases = (
            ((range(5), 1), 3),
            ((np.nan, 1), np.nan),
            ((range(5), np.nan), np.nan),
            (([1.1, 2.2, 3.3], 1), 5. / 3),
            ((range(5), .5), 6),
        )


def _make_level_sets_cases():
    nlevelss = (2, 5, 500)
    # for each number of levels, insert one object per level into the matrix, such that it will be dilated to a 3x3
    # square and then eroded to a single pixel
    for nlevels in nlevelss:
        # test only vertical extension:
        # . . .
        # 0 0 0
        # 1 1 1
        # 0 0 0
        # . . .
        im = np.zeros((nlevels * 4 + 3, 3))
        for i in range(nlevels):
            r = 4 * i + 1
            im[(r, r, r), (0, 1, 2)] = 1 - float(i) / nlevels
        yield ((im, nlevels), np.concatenate((np.arange(nlevels, 1, -1), np.zeros(1))))

        # test mainly vertical extension but surround with sufficient zeros
        # . . . . .
        # 0 0 0 0 0
        # 0 1 1 1 0
        # 0 0 0 0 0
        # . . . . .
        im = np.zeros((nlevels * 4 + 4, 7))
        for i in range(nlevels):
            r = 4 * i + 2
            im[(r, r, r), (2, 3, 4)] = 1 - float(i) / nlevels
        yield ((im, nlevels), np.concatenate((np.arange(nlevels, 1, -1), np.zeros(1))))

        # test both vertical and horizontal extension with surrounding zeros
        # . . . . . . .
        # 0 0 0 0 0 0 0
        # 0 0 0 1 0 0 0
        # 0 0 0 1 0 0 0
        # 0 0 1 0 1 0 0
        # 0 0 0 0 0 0 0
        # . . . . . . .
        im = np.zeros((nlevels * 6 + 6, 7))
        for i in range(nlevels):
            r = 6 * i + 3
            im[(r - 1, r, r + 1, r + 1), (3, 3, 2, 4)] = 1 - float(i) / nlevels
        yield ((im, nlevels), np.concatenate((np.arange(nlevels, 1, -1), np.zeros(1))))

    # non-monotonic case where an objects splits into two in the second level and one of them disappears in the highest
    # level
    im = np.zeros((9, 5))
    im[2, 1:4] = 1
    im[4, 1:4] = 0.4
    im[6, 1:4] = 0.6
    yield ((im, 3), [1, 2, 0])


if __name__ == '__main__':
    unittest.main()
