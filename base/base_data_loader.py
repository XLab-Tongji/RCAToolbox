from abc import ABC, abstractmethod


class BaseDataLoader(ABC):
    """
    data_loader(读取运维数据)的基类.

    Attributes:
        train_data: 有监督的训练数据，半监督/无监督下的基准数据（一般为正常数据）.
        valid_data: 数据源.
        test_data: 测试数据.
    """

    def __init__(self):
        self.train_data = dict()
        self.valid_data = dict()
        self.test_data = dict()

    @abstractmethod
    def load_data(self, rca_model_name, dataset):
        """
        根据算法的配置文件加载数据集，配置文件中的train、valid、test字段分别标识了不同种类的实验

        :param rca_model_name: str，采用的rca模型名称.
        :param dataset: str，数据集名称.
        """
        raise NotImplementedError
