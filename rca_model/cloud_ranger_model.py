from base.base_rca_model import BaseRCAModel
from utils.data_helper import normalize
from causality.inference.search import IC
from causality.inference.independence_tests import RobustRegressionTest
import pandas as pd
import numpy as np


class CloudRangerModel(BaseRCAModel):
    """
    CloudRanger RCA模型.
    """

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_metric_data(data):
        """

        :param data: DataLoader读出的所有数据
        :return: metric数据二维矩阵
        """
        metric_data = data['metric']
        metric_sample_list = [metric_data[i].sample['value'] for i in range(len(metric_data))]
        metric_sample_matrix = np.array(metric_sample_list)
        idx = np.argwhere(np.all(metric_sample_matrix[..., :] == 0, axis=1))
        metric_sample_matrix = np.delete(metric_sample_matrix, idx, axis=0)
        return metric_sample_matrix

    @staticmethod
    def build_impact_graph(data, alpha):
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

    @staticmethod
    def build_correlation_matrix(data):
        """
        计算取绝对值后的Pearson相关系数.

        :param data: 数据集
        :return: 相关系数矩阵
        """
        return np.abs(np.corrcoef(np.array(data)))

    @staticmethod
    def build_prob_matrix(impact_graph, correlation_matrix, front_end, beta, rho):
        """
        构建边的转移概率矩阵.

        :param impact_graph: PC算法构建出的影响图
        :param correlation_matrix: Pearson相关系数矩阵
        :param front_end: 前端节点
        :param beta: 前一个节点的影响强度
        :param rho: 后一个节点的影响强度
        :return: 边的转移概率矩阵
        """

        node_num = len(impact_graph)

        # 节点和边的转移概率矩阵P、M
        node_trans_prob = np.zeros((node_num, node_num))
        edge_trans_prob = np.zeros((node_num, node_num, node_num))

        # 遍历临接边
        for i in range(node_num):
            for j in range(node_num):
                if impact_graph[i][j] == 1:
                    node_trans_prob[i, j] = impact_graph[i][j] * correlation_matrix[j, front_end - 1]

        # P按列归一化
        node_trans_prob = normalize(node_trans_prob, axis=0)

        # 遍历出边，得到向前转移的概率
        for k in range(node_num):
            for i in range(node_num):
                for j in range(node_num):
                    if impact_graph[i][j] == 1:
                        edge_trans_prob[k, i, j] = ((1 - beta) * node_trans_prob[k][i] + beta * node_trans_prob[i][j])

        # M归一化
        edge_trans_prob = normalize(edge_trans_prob, axis=2)

        # 遍历入边，得到向后转移的概率
        for k in range(node_num):
            for i in range(node_num):
                for j in range(node_num):
                    if impact_graph[i][j] == 0 and impact_graph[j][i] == 1:
                        edge_trans_prob[k, i, j] = ((1 - beta) * node_trans_prob[k][i] + beta * node_trans_prob[i][j])

        # M归一化，并乘向后转移系数
        edge_trans_prob = normalize(edge_trans_prob, axis=2)
        edge_trans_prob *= rho

        # 生成自环，得到原地转移概率
        for k in range(node_num):
            for i in range(node_num):
                if edge_trans_prob[k, i, i] == 0:
                    in_out_node = list(range(node_num))
                    in_out_node.remove(i)
                    edge_trans_prob[k, i, i] = max(0, impact_graph[front_end - 1][i] -
                                                   max(edge_trans_prob[k, i, in_out_node]))
        # M归一化
        edge_trans_prob = normalize(edge_trans_prob, axis=2)

        return edge_trans_prob

    def build(self, train_data, config):
        """
        使用CloudRanger框架构建RCA模型.

        :param train_data: 训练数据，与base/base_data_loader.py中读入的train_data格式一致.
        :param config: 模型参数.
        :return 如果是每组实验一个模型，返回一个dict，key为experiment_id；如果是训练集整个是一个模型，返回该模型.
        """
        model = dict()

        for experiment_id, data in train_data.items():
            metric_sample_matrix = self.get_metric_data(data)
            impact_graph = self.build_impact_graph(metric_sample_matrix, config['alpha'])
            correlation_matrix = self.build_correlation_matrix(metric_sample_matrix)
            prob_matrix = self.build_prob_matrix(impact_graph, correlation_matrix, config['front_end'],
                                                 config['beta'], config['rho'])
            model[experiment_id] = {'G': impact_graph, 'M': prob_matrix}

        return model
