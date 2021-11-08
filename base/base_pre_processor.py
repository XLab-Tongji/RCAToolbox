from abc import ABC, abstractmethod


class BasePreProcessor(ABC):
    """
    pre_processor(数据预处理)的基类.
    """

    def __init__(self):
        pass

    @abstractmethod
    def metric_pre_processor(self, metric_list):
        """
        预处理metric数据

        :param metric_list: list，一组实验中的metric数据.
        :return list，预处理完成后的metric数据.
        """
        raise NotImplementedError

    @abstractmethod
    def tracing_pre_processor(self, tracing_list):
        """
        预处理tracing数据

        :param tracing_list: list，一组实验中的tracing数据.
        :return list，预处理完成后的tracing数据.
        """
        raise NotImplementedError

    @abstractmethod
    def logging_pre_processor(self, logging_list):
        """
        预处理logging数据

        :param logging_list: list，一组实验中的logging数据.
        :return list，预处理完成后的tracing数据.
        """
        raise NotImplementedError
