import numpy as np

from utils import random_walk
from base.base_localization import BaseLocalization


class MonitorRankLocalization(BaseLocalization):
    """
    使用monitor_rank进行根因定位
    """

    @staticmethod
    def firstorder_randomwalk(
            rca_model,
            epoches,
            start_node,
            teleportation_prob,
            walk_step=1000,
            print_trace=False,
    ):
        """
                  根据训练集中的数据构建根因分析模型.
                  :param rca_model: 构建好的根因分析模型,传入的应该是一个类似于矩阵的变量
                  :param epoches: 迭代次数
                  :param start_node:游走开始节点
                  :param teleportation_prob:当算法陷入出度为0的节点，依照概率跳转到其他节点。
                  :param walk_step:游走步长
                  :param print_trace:是否打印轨迹
                  :return dict，每组实验定位的结果，key为experiment_id，value类型为list，其中的每个元素为元组，第一个维度标识根因，第二个维度标识可能性（或评判可能性的依据），按可能性由大到小排列.
                """
        label = [i for i in range(len(rca_model))]
        n = rca_model.shape[0]
        score = np.zeros([n])
        current = start_node - 1
        for epoch in range(epoches):
            if print_trace:
                print("\n{:2d}".format(current + 1), end="->")
            for step in range(walk_step):
                if np.sum(rca_model[current]) == 0:
                    current = np.random.choice(range(n), p=teleportation_prob)
                    break
                else:
                    next_node = np.random.choice(range(n), p=rca_model[current])
                    if print_trace:
                        print("{:2d}".format(current + 1), end="->")
                    score[next_node] += 1
                    current = next_node
        score_list = list(zip(label, score))
        score_list.sort(key=lambda x: x[1], reverse=True)
        return score_list

    def localize(self, rca_model, data, config):
        """
          根据训练集中的数据构建根因分析模型.
          :param rca_model: 构建好的根因分析模型.
          :param data: 验证集或测试集数据，与base/base_data_loader.py中读入的valid_data、test_data格式一致.
          :param config: 模型参数.
          :return dict，每组实验定位的结果，key为experiment_id，value类型为list，其中的每个元素为元组，第一个维度标识根因，第二个维度标识可能性（或评判可能性的依据），按可能性由大到小排列.
        """

        result = dict()
        for experiment_id in rca_model.keys():
            result[experiment_id] = random_walk.first_order_random_walk(rca_model[experiment_id]['pc_graph'], config['rank_paces'],
                                                               config['frontend'],
                                                               rca_model[experiment_id]['teleportation_prob'],
                                                               config['walk_step'], print_trace=False,)
        return result
