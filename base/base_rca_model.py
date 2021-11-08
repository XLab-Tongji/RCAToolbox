from abc import ABC, abstractmethod


class BaseRCAModel(ABC):
    """
    根因分析模型的基类.
    """

    def __init__(self):
        pass

    @abstractmethod
    def build(self, train_data, config):
        """
        根据训练集中的数据构建根因分析模型.

        :param train_data: 训练数据，与base/base_data_loader.py中读入的train_data格式一致.
        :param config: 模型参数.
        :return 如果是每组实验一个模型，返回一个dict，key为experiment_id；如果是训练集整个是一个模型，返回该模型.
        """
        raise NotImplementedError
