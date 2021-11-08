from base.base_pre_processor import BasePreProcessor
from utils.data_helper import linearly_interpolate_nans


class DemoPreProcessor(BasePreProcessor):
    """
    demo数据集的预处理模块.
    """

    def __init__(self):
        super().__init__()

    def metric_pre_processor(self, metric_list):
        """
        预处理metric数据

        :param metric_list: list，一组实验中的metric数据.
        :return list，预处理完成后的metric数据.
        """
        result_list = []
        for metric in metric_list:
            # TODO: 根据Prometheus特性增加差分
            metric.sample['value'] = linearly_interpolate_nans(metric.sample['value'])
            result_list.append(metric)
        return result_list

    def tracing_pre_processor(self, tracing_list):
        """
        预处理tracing数据

        :param tracing_list: list，一组实验中的tracing数据.
        :return list，预处理完成后的tracing数据.
        """
        result_list = []
        ...
        return result_list

    def logging_pre_processor(self, logging_list):
        """
        预处理logging数据

        :param logging_list: list，一组实验中的logging数据.
        :return list，预处理完成后的tracing数据.
        """
        result_list = []
        ...
        return result_list
