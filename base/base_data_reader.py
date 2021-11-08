from abc import ABC, abstractmethod
import os


class BaseDataReader(ABC):
    """
    读取可观察数据的基类.

    Attributes:
        dataset_base_path: 数据集的基础路径.
    """
    def __init__(self):
        self.dataset_base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'data')

    @abstractmethod
    def metric_reader(self, dataset, experiment_id):
        """
        读取metric数据

        :param dataset: str，数据集名称.
        :param experiment_id: str，实验标识.
        """
        raise NotImplementedError

    @abstractmethod
    def tracing_reader(self, dataset, experiment_id):
        """
        读取tracing数据

        :param dataset: str，数据集名称.
        :param experiment_id: str，实验标识.
        """
        raise NotImplementedError

    @abstractmethod
    def logging_reader(self, dataset, experiment_id):
        """
        读取logging数据

        :param dataset: str，数据集名称.
        :param experiment_id: str，实验标识.
        """
        raise NotImplementedError
