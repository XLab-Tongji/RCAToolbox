import os
import json
import pandas as pd
import numpy as np
from data_model.metric_data_model import MetricDataModel
from base.base_data_reader import BaseDataReader


class StandardDataReader(BaseDataReader):
    """
    读取可观察数据的标准类.
    """
    def __init__(self):
        super().__init__()

    def metric_reader(self, dataset, experiment_id):
        """
        读取metric数据

        :param dataset: str，数据集名称.
        :param experiment_id: str，实验标识.
        :return: list，每个element为遵循data_model/metric_data_model.py中MetricDataModel及其子类的metric信息.
        """
        result_list = []

        metric_file_path = os.path.join(self.dataset_base_path, dataset, 'metric', experiment_id + '.csv')
        if not os.path.exists(metric_file_path):
            # TODO: 添加异常日志记录信息
            ...
            return result_list

        metric_file = pd.read_csv(metric_file_path)
        name_list = metric_file.columns.values
        for name in name_list:
            if name == "datetime" or name == "timestamp":
                continue
            metric_data = MetricDataModel()
            metric_data.name = name
            metric_data.sample['timestamp'] = list(metric_file['timestamp'].values)
            metric_data.sample['value'] = np.array(metric_file[name].values)
            result_list.append(metric_data)

        return result_list

    def tracing_reader(self, dataset, experiment_id):
        """
        读取tracing数据

        :param dataset: str，数据集名称.
        :param experiment_id: str，实验标识.
        """
        tracing_base_path = os.path.join(self.dataset_base_path, dataset, 'tracing')
        return []

    def logging_reader(self, dataset, experiment_id):
        """
        读取logging数据

        :param dataset: str，数据集名称.
        :param experiment_id: str，实验标识.
        """
        logging_base_path = os.path.join(self.dataset_base_path, dataset, 'logging')
        return []

    def label_reader(self, dataset, experiment_id):
        """
        读取label数据

        :param dataset: str，数据集名称.
        :param experiment_id: str，实验标识.
        """
        label_file_path = os.path.join(self.dataset_base_path, dataset, 'label.json')
        with open(label_file_path) as f:
            label_dict = json.load(f)
        return label_dict[experiment_id]

