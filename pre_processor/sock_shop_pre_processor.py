from base.base_pre_processor import BasePreProcessor
from utils.data_helper import linearly_interpolate_nans
import pandas as pd


class SockShopPreProcessor(BasePreProcessor):
    """
    demo数据集的预处理模块.
    """

    def __init__(self):
        super().__init__()

    def metric_pre_processor(self, metric_list):
        """
        预处理sock-shop数据集的metric数据，处理Nan值后进行二阶差分。

        :param metric_list: list，一组实验中的metric数据.
        :return list，预处理完成后的metric数据.
        """
        result_list = []

        # Prometheus的特性：30s采样一次
        diff_len = 30
        # 二阶差分
        diff_order = 2

        for metric in metric_list:
            metric.sample['value'] = linearly_interpolate_nans(metric.sample['value'])
            temp = pd.Series(metric.sample['value'])
            for order in range(diff_order):
                temp = linearly_interpolate_nans(temp.diff(periods=diff_len))
            metric.sample['value'] = temp.values
            result_list.append(metric)
        return result_list

    def tracing_pre_processor(self, tracing_list):
        """
        预处理sock-shop数据集的tracing数据

        :param tracing_list: list，一组实验中的tracing数据.
        :return list，预处理完成后的tracing数据.
        """
        result_list = []
        ...
        return result_list

    def logging_pre_processor(self, logging_list):
        """
        预处理sock-shop数据集的logging数据

        :param logging_list: list，一组实验中的logging数据.
        :return list，预处理完成后的tracing数据.
        """
        result_list = []
        ...
        return result_list
