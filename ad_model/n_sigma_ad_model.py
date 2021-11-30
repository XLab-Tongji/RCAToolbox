from base.base_ad_model import BaseADModel
import numpy as np


class NSigmaADModel(BaseADModel):
    """
    根据设定的标准差倍数进行异常检测.
    """

    def __init__(self):
        super().__init__()
        self.model = dict()
        self.n = 3
        self.window_size = 1
        self.correct_interval = {
            'start': 180,
            'end': 300
        }

    def detect_anomaly(self, data, mode, experiment_id, strip_correct_interval=True):
        """
        n sigma异常检测

        :param data: dict，表征metric，与data_model/metric_data_model.py中的结构相同.
        :param mode: 异常检测模式，只检测第一个（取值为single）还是全部的（all）异常点.
        :param experiment_id: 实验信息，针对每一个实验中的相关数据分别载入构建好的异常检测模型.
        :param strip_correct_interval: 是否需要去除correct_interval中的部分（去掉正常部分）.
        :return list，元素为异常时间点对应的时间戳，如果list为空证明检测的数据是正常的.
        """
        result_list = []

        low_threshold = self.model[experiment_id][data.name]['low_threshold']
        high_threshold = self.model[experiment_id][data.name]['high_threshold']
        
        anomaly_index = (np.where((data.sample['value'] > high_threshold) |
                                  (data.sample['value'] < low_threshold)) + data.sample['timestamp'][0])[0]

        if strip_correct_interval:
            anomaly_index = anomaly_index[anomaly_index > data.sample['timestamp'][0] + self.correct_interval['end']]

        anomaly_list = anomaly_index.tolist()
        if len(anomaly_list) > 0:
            if mode == 'single':
                result_list.append(anomaly_list[0])
            elif mode == 'all':
                result_list = anomaly_list
        return result_list

    def build_anomaly_model(self, data, experiment_id):
        """
        根据正常区间，构建异常点的上界和下界

        :param data: dict，表征metric，与data_model/metric_data_model.py中的结构相同.
        :param experiment_id: 实验信息，针对每一个实验中的相关数据分别构建异常检测模型.
        """
        if experiment_id not in self.model.keys():
            self.model[experiment_id] = dict()

        if data.name not in self.model[experiment_id].keys():
            self.model[experiment_id][data.name] = {
                'low_threshold': '',
                'high_threshold': ''
            }

        y_mean = np.mean(data.sample['value'][self.correct_interval['start']:self.correct_interval['end']])
        y_std = np.std(data.sample['value'][self.correct_interval['start']:self.correct_interval['end']])
        self.model[experiment_id][data.name]['low_threshold'] = y_mean - self.n * y_std
        self.model[experiment_id][data.name]['high_threshold'] = y_mean + self.n * y_std
