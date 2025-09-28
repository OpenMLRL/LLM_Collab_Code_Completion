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