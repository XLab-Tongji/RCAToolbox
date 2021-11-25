from causality.inference.search import IC
from causality.inference.independence_tests import RobustRegressionTest
import pandas as pd


def build_graph_pc(data, alpha):
    """
    通过PC算法构建影响图

    :param data: 数据集
    :param alpha: 显著性水平，用于进行条件独立性判断
    :return: impact graph的矩阵表示
    """
    # 数据预处理
    metric_num = len(data)
    labeled_data = dict()
    variable_types = dict()
    for i in range(metric_num):
        labeled_data[str(i)] = data[i]
        variable_types[str(i)] = 'c'
    labeled_data = pd.DataFrame(labeled_data)

    # 通过PC算法构建DAG
    ic_algorithm = IC(RobustRegressionTest, alpha=alpha)
    graph = ic_algorithm.search(labeled_data, variable_types)

    # 将graph转化为01矩阵表示
    graph_matrix = [[0] * metric_num for _ in range(metric_num)]
    for u, v in graph.edges:
        graph_matrix[int(u)][int(v)] = 1
    return graph_matrix
