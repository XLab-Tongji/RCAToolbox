import numpy as np


class ADUtils:
    """
    通用的一些异常检测的工具函数
    """

    @staticmethod
    def get_metric_data(data):
        """
        从data（字典）中提取数据，有service的名字；service数据的矩阵
        :param data: DataLoader读出的所有数据
        :return: 二元元组，包括metric名称列表及数据二维矩阵
        """
        metric_data = data['metric']
        header = [metric_data[i].name for i in range(len(metric_data))]
        metric_sample_list = [metric_data[i].sample['value'] for i in range(len(metric_data))]
        metric_sample_matrix = np.array(metric_sample_list)
        idx = np.argwhere(np.all(metric_sample_matrix[..., :] == 0, axis=1))
        metric_sample_matrix = np.delete(metric_sample_matrix, idx, axis=0)
        header = np.delete(header, idx, axis=0)
        return header, metric_sample_matrix

    @staticmethod
    def ad_metric_find_first_timestamp(ad_model, metric_list, experiment_id):
        """
        检测metric列表中最开始的异常时间

        :param ad_model: 异常检测模型实例，参见base/base_ad_model.py.
        :param metric_list: 需要检测的异常metric列表.
        :param experiment_id: 实验标识信息.
        :return: list，如存在异常，则list中只包含一个元素，为最初的异常时间点，反之为空.
        """
        # 防止一个异常都没有
        detected = False
        first_timestamp = metric_list[0].sample['timestamp'][-1]
        metric_name = ''
        for metric in metric_list:
            temp_timestamp_list = ad_model.detect_anomaly(metric, 'single', experiment_id)
            if len(temp_timestamp_list) == 0:
                continue
            detected = True
            if temp_timestamp_list[0] < first_timestamp:
                first_timestamp = temp_timestamp_list[0]
                metric_name = metric.name
        if not detected:
            return []
        return [(first_timestamp, metric_name)]

    @staticmethod
    def ad_metric_filter(ad_model, metric_list, start_timestamp, end_timestamp, experiment_id):
        """
        筛选异常的metric指标，同时截取需要分析的部分

        :param ad_model: 异常检测模型实例，参见base/base_ad_model.py.
        :param metric_list: metric列表.
        :param start_timestamp: 需要截取分析的开始时间戳.
        :param end_timestamp: 需要截取分析的终止时间戳.
        :param experiment_id: 实验标识信息.
        :return: list，截取后的异常metric列表.
        """
        result_list = []
        for metric in metric_list:
            start_index = metric.sample['timestamp'].index(start_timestamp)
            end_index = metric.sample['timestamp'].index(end_timestamp)

            metric.sample['timestamp'] = metric.sample['timestamp'][start_index:end_index]
            metric.sample['value'] = metric.sample['value'][start_index:end_index]

            temp_timestamp_list = ad_model.detect_anomaly(metric, 'single', experiment_id, False)
            if len(temp_timestamp_list) == 0:
                continue
            else:
                result_list.append(metric)

        return result_list

    @staticmethod
    def get_martix(data):
        """
        将字典里的数据展开为一个矩阵
        :param data: 读取到的data，是个字典
        :return: 一个展开的矩阵
        """
        x = len(data['metric'])
        y = len(data['metric'][0].sample['value'])
        matrix = np.zeros((y, x))
        i = 0
        j = 0
        for item in data['metric']:
            for value in item.sample['value']:
                matrix[j][i] = value
                j += 1
            i += 1
            j = 0
        return matrix
