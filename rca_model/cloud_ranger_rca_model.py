from base.base_rca_model import BaseRCAModel
from utils.ad_utils import ADUtils
from utils.data_helper import normalize
from utils.build_graph import build_graph_pc
import csv
import os
import numpy as np
import pandas as pd


class CloudRangerModel(BaseRCAModel):
    """
    CloudRanger RCA模型.
    """

    def __init__(self):
        super().__init__()

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

        for experiment_id, data in train_data['data'].items():
            if len(train_data['data'][experiment_id]['metric']) == 0:
                continue
            header, metric_sample_matrix = ADUtils.get_metric_data(data)
            entry = train_data['entry_metric_name'][experiment_id]
            front_end = np.where(header == entry)[0][0]

            saved_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                                      'saved/model/cloud_ranger_runner/alpha_0_05/impact_graph')
            full_path = os.path.join(saved_path, f"{experiment_id}.csv")

            if not os.path.exists(full_path):
                impact_graph = build_graph_pc(metric_sample_matrix, config['alpha'])
                with open(full_path, 'w+') as file:
                    writer = csv.writer(file)
                    writer.writerows(impact_graph)
            else:
                data_list = pd.read_csv(full_path)
                impact_graph = data_list.values.tolist()

            correlation_matrix = self.build_correlation_matrix(metric_sample_matrix)
            prob_matrix = self.build_prob_matrix(impact_graph, correlation_matrix, front_end,
                                                 config['beta'], config['rho'])
            model[experiment_id] = {'G': impact_graph, 'M': prob_matrix, 'header': header,
                                    'front_end': front_end}

        return model
