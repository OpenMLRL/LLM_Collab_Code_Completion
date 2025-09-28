import numpy as np


class MetricsCalculator2:
    """
    The class provides to calculate Mean Reciprocal Rank (MRR) and Mean Average Precision (MAP) based on input data, where MRR measures the ranking quality and MAP measures the average precision.
    """

    def __init__(self):
        pass

    @staticmethod
    def mrr(data):
        if isinstance(data, list):
            results = []
            for item in data:
                if isinstance(item, tuple) and len(item) == 2:
                    result_list, ground_truth = item
                    if not isinstance(result_list, list):
                        result_list = list(result_list)
                    if not isinstance(ground_truth, int):
                        ground_truth = int(ground_truth)
                    if ground_truth <= 0:
                        results.append(0.0)
                        continue
                    for i, val in enumerate(result_list):
                        if val == 1:
                            reciprocal_rank = 1.0 / (i + 1)
                            results.append(reciprocal_rank)
                            break
                    else:
                        results.append(0.0)
            return np.mean(results), results
        else:
            if isinstance(data, tuple) and len(data) == 2:
                result_list, ground_truth = data
                if not isinstance(result_list, list):
                    result_list = list(result_list)
                if not isinstance(ground_truth, int):
                    ground_truth = int(ground_truth)
                if ground_truth <= 0:
                    return 0.0, [0.0]
                for i, val in enumerate(result_list):
                    if val == 1:
                        reciprocal_rank = 1.0 / (i + 1)
                        return reciprocal_rank, [reciprocal_rank]
                return 0.0, [0.0]
            else:
                return 0.0, [0.0]

    @staticmethod
    def map(data):
        if isinstance(data, list):
            results = []
            for item in data:
                if isinstance(item, tuple) and len(item) == 2:
                    result_list, ground_truth = item
                    if not isinstance(result_list, list):
                        result_list = list(result_list)
                    if not isinstance(ground_truth, int):
                        ground_truth = int(ground_truth)
                    if ground_truth <= 0:
                        results.append(0.0)
                        continue
                    ap = 0.0
                    relevant = 0
                    for i, val in enumerate(result_list):
                        if val == 1:
                            relevant += 1
                            ap += (relevant / (i + 1))
                    if relevant == 0:
                        results.append(0.0)
                    else:
                        results.append(ap / ground_truth)
            return np.mean(results), results
        else:
            if isinstance(data, tuple) and len(data) == 2:
                result_list, ground_truth = data
                if not isinstance(result_list, list):
                    result_list = list(result_list)
                if not isinstance(ground_truth, int):
                    ground_truth = int(ground_truth)
                if ground_truth <= 0:
                    return 0.0, [0.0]
                ap = 0.0
                relevant = 0
                for i, val in enumerate(result_list):
                    if val == 1:
                        relevant += 1
                        ap += (relevant / (i + 1))
                if relevant == 0:
                    return 0.0, [0.0]
                else:
                    return (ap / ground_truth), [ap / ground_truth]
            else:
                return 0.0, [0.0]

import unittest


class MetricsCalculator2TestMrr(unittest.TestCase):
    def test_mrr_1(self):
        mc2 = MetricsCalculator2()
        res1, res2 = MetricsCalculator2.mrr(([1, 0, 1, 0], 4))
        self.assertEqual(res1, 1.0)
        self.assertEqual(res2, [1.0])

    def test_mrr_2(self):
        res1, res2 = MetricsCalculator2.mrr(([0, 0, 0, 1], 4))
        self.assertEqual(res1, 0.25)
        self.assertEqual(res2, [0.25])

    def test_mrr_3(self):
        res1, res2 = MetricsCalculator2.mrr([([1, 0, 1, 0], 4), ([0, 1, 0, 1], 4)])
        self.assertEqual(res1, 0.75)
        self.assertEqual(res2, [1.0, 0.5])

    def test_mrr_4(self):
        res1, res2 = MetricsCalculator2.mrr([([1, 1, 1, 0], 4), ([0, 0, 0, 1], 4)])
        self.assertEqual(res1, 0.625)
        self.assertEqual(res2, [1.0, 0.25])

    def test_mrr_5(self):
        res1, res2 = MetricsCalculator2.mrr([([1, 0, 1, 1], 4), ([0, 1, 0, 0], 4)])
        self.assertEqual(res1, 0.75)
        self.assertEqual(res2, [1.0, 0.5])

    def test_mrr_6(self):
        try:
            MetricsCalculator2.mrr(1)
        except:
            pass

    def test_mrr_7(self):
        res1, res2 = MetricsCalculator2.mrr([])
        self.assertEqual(res1, 0.0)
        self.assertEqual(res2, [0.0])

    def test_mrr_8(self):
        res1, res2 = MetricsCalculator2.mrr([([1, 0, 1, 1], 0), ([0, 1, 0, 0], 0)])
        self.assertEqual(res1, 0.0)
        self.assertEqual(res2, [0.0, 0.0])


class MetricsCalculator2TestMap(unittest.TestCase):
    def test_map_1(self):
        res1, res2 = MetricsCalculator2.map(([1, 0, 1, 0], 4))
        self.assertEqual(res1, 0.41666666666666663)
        self.assertEqual(res2, [0.41666666666666663])

    def test_map_2(self):
        res1, res2 = MetricsCalculator2.map(([0, 0, 0, 1], 4))
        self.assertEqual(res1, 0.0625)
        self.assertEqual(res2, [0.0625])

    def test_map_3(self):
        res1, res2 = MetricsCalculator2.map([([1, 0, 1, 0], 4), ([0, 1, 0, 1], 4)])
        self.assertEqual(res1, 0.3333333333333333)
        self.assertEqual(res2, [0.41666666666666663, 0.25])

    def test_map_4(self):
        res1, res2 = MetricsCalculator2.map([([1, 1, 1, 0], 4), ([0, 0, 0, 1], 4)])
        self.assertEqual(res1, 0.40625)
        self.assertEqual(res2, [0.75, 0.0625])

    def test_map_5(self):
        res1, res2 = MetricsCalculator2.map([([1, 0, 1, 1], 4), ([0, 1, 0, 0], 4)])
        self.assertEqual(res1, 0.3645833333333333)
        self.assertEqual(res2, [0.6041666666666666, 0.125])

    def test_map_6(self):
        try:
            MetricsCalculator2.map(1)
        except:
            pass

    def test_map_7(self):
        res1, res2 = MetricsCalculator2.map([])
        self.assertEqual(res1, 0.0)
        self.assertEqual(res2, [0.0])

    def test_map_8(self):
        res1, res2 = MetricsCalculator2.map([([1, 0, 1, 1], 0), ([0, 1, 0, 0], 0)])
        self.assertEqual(res1, 0.0)
        self.assertEqual(res2, [0.0, 0.0])


class MetricsCalculator2Test(unittest.TestCase):
    def test_metricscalculator2_1(self):
        res1, res2 = MetricsCalculator2.mrr(([1, 0, 1, 0], 4))
        self.assertEqual(res1, 1.0)
        self.assertEqual(res2, [1.0])

    def test_metricscalculator2_2(self):
        res1, res2 = MetricsCalculator2.mrr([([1, 0, 1, 0], 4), ([0, 1, 0, 1], 4)])
        self.assertEqual(res1, 0.75)
        self.assertEqual(res2, [1.0, 0.5])

    def test_metricscalculator2_3(self):
        res1, res2 = MetricsCalculator2.map(([1, 0, 1, 0], 4))
        self.assertEqual(res1, 0.41666666666666663)
        self.assertEqual(res2, [0.41666666666666663])

    def test_metricscalculator2_4(self):
        res1, res2 = MetricsCalculator2.map([([1, 0, 1, 0], 4), ([0, 1, 0, 1], 4)])
        self.assertEqual(res1, 0.3333333333333333)
        self.assertEqual(res2, [0.41666666666666663, 0.25])