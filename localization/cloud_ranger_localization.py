from base.base_localization import BaseLocalization
import numpy as np


class CloudRangerLocalization(BaseLocalization):
    """
    CloudRanger 根因定位.
    """

    @staticmethod
    def second_order_random_walk(header, edge_trans_prob, epochs, front_end, steps):
        """
        二阶随机游走算法

        :param header: 数据头，即服务名
        :param edge_trans_prob: 边转移概率矩阵
        :param epochs: 轮数
        :param front_end: 前端节点
        :param steps: 单轮随机游走步数
        :return: 相关性得分列表，按分数降序排列
        """
        n = edge_trans_prob.shape[0]
        score = np.zeros([n])
        for epoch in range(epochs):
            previous = front_end - 1
            current = front_end - 1
            for step in range(steps):
                if np.sum(edge_trans_prob[previous, current]) == 0:
                    break
                next_node = np.random.choice(range(n), p=edge_trans_prob[previous, current])
                score[next_node] += 1
                previous = current
                current = next_node
        score_list = list(zip(header, score))

        # 排序 并排除score为0的项
        score_list.sort(key=lambda x: x[1], reverse=True)
        for index, pair in enumerate(score_list):
            if pair[1] == 0:
                score_list = score_list[0:index]
                break
        return score_list

    def localize(self, rca_model, data, config):
        """
        根据训练集中的数据构建根因分析模型.

        :param rca_model: 构建好的根因分析模型.
        :param data: 验证集或测试集数据，与base/base_data_loader.py中读入的valid_data、test_data格式一致.
        :param config: 模型参数.
        :return dict，每组实验定位的结果，key为experiment_id，value类型为list，其中的每个元素为元组，第一个维度标识根因，第二个维度标识可能性（或评判可能性的依据），按可能性由大到小排列.
        """
        result_dict = dict()

        for experiment_id, data in data.items():
            model = rca_model[experiment_id]
            result_dict[experiment_id] = self.second_order_random_walk(model['header'], model['M'], config['epochs'],
                                                                       config['front_end'], config['steps'])
        return result_dict
