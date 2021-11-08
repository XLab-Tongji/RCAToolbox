from abc import ABC, abstractmethod


class BaseLocalization(ABC):
    """
    定位根因的基类.
    """

    def __init__(self):
        pass

    @abstractmethod
    def localize(self, rca_model, data, config):
        """
        根据训练集中的数据构建根因分析模型.

        :param rca_model: 构建好的根因分析模型.
        :param data: 验证集或测试集数据，与base/base_data_loader.py中读入的valid_data、test_data格式一致.
        :param config: 模型参数.
        :return dict，每组实验定位的结果，key为experiment_id，value类型为list，其中的每个元素为元组，第一个维度标识根因，第二个维度标识可能性（或评判可能性的依据），按可能性由大到小排列.
        """
        raise NotImplementedError
