from base.base_localization import BaseLocalization
from utils.random_walk import first_order_random_walk, second_order_random_walk
import numpy as np


class RandomWalkLocalization(BaseLocalization):
    """
    随机游走的根因定位
    """

    def __init__(self, order: int):
        """
        Args:
            order: 随机游走阶数
        """
        super().__init__()
        self.order = order

    def localize(self, rca_model, data, config):
        """
        根据训练集中的数据构建根因分析模型.
        :param rca_model: 构建好的根因分析模型.
        :param data: 验证集或测试集数据，与base/base_data_loader.py中读入的valid_data、test_data格式一致.
        :param config: 模型参数.
        :return dict，每组实验定位的结果，key为experiment_id，value类型为list，其中的每个元素为元组，第一个维度标识根因，第二个维度标识可能性（或评判可能性的依据），按可能性由大到小排列.
        """
        result_dict = dict()
        for experiment_id, test_data in data['data'].items():
            if len(data['data'][experiment_id]['metric']) == 0:
                result_dict[experiment_id] = []
                continue
            model = rca_model[experiment_id]
            front_end = np.where(model['header'] == (model['entry']))[0][0]
            if self.order == 1:
                # front_end = model['frontend'][experiment_id]
                result_dict[experiment_id] = first_order_random_walk(model['header'],rca_model[experiment_id]['pc_graph'],
                                                                     config['epochs'],
                                                                     front_end,
                                                                     rca_model[experiment_id]['teleportation_prob'],
                                                                     config['walk_step'], print_trace=False, )
            elif self.order == 2:
                front_end = np.where(model['header'] == (model['entry']))[0][0]
                result_dict[experiment_id] = second_order_random_walk(model['header'], model['M'], config['epochs'],
                                                                      front_end, config['steps'])

        return result_dict
