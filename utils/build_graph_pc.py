from causality.inference.search import IC
from causality.inference.independence_tests import RobustRegressionTest
import pandas as pd


def build_graph_pc(data, alpha):
    node_num = len(data)
    x = dict()
    variable_types = dict()
    for i in range(node_num):
        x[str(i)] = data[i]
        variable_types[str(i)] = 'c'
    x = pd.DataFrame(x)
# pc算法，以上提取到预处理中
    # run the search
    ic_algorithm = IC(RobustRegressionTest, alpha=alpha)
    graph = ic_algorithm.search(x, variable_types)
# pc算法，以下也要提取
    n = [[0]*node_num for _ in range(node_num)]
    for u, v in graph.edges:
        n[int(u)][int(v)] = 1
    return n
