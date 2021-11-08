class ADUtils:
    """
    通用的一些异常检测的工具函数
    """

    @staticmethod
    def ad_metric_find_first_timestamp(ad_model, metric_list):
        """
        检测metric列表中最开始的异常时间

        :param ad_model: 异常检测模型实例，参见base/base_ad_model.py.
        :param metric_list: 需要检测的异常metric列表.
        :return: list，如存在异常，则list中只包含一个元素，为最初的异常时间点，反之为空.
        """
        # 防止一个异常都没有
        detected = False
        first_timestamp = metric_list[0].sample['timestamp'][-1]
        for metric in metric_list:
            temp_timestamp_list = ad_model.detect_anomaly(metric, 'single')
            if len(temp_timestamp_list) == 0:
                continue
            detected = True
            if temp_timestamp_list[0] < first_timestamp:
                first_timestamp = temp_timestamp_list[0]
        if not detected:
            return []
        return [first_timestamp]

    @staticmethod
    def ad_metric_filter(ad_model, metric_list, start_timestamp, end_timestamp):
        """
        筛选异常的metric指标，同时截取需要分析的部分

        :param ad_model: 异常检测模型实例，参见base/base_ad_model.py.
        :param metric_list: metric列表.
        :param start_timestamp: 需要截取分析的开始时间戳.
        :param end_timestamp: 需要截取分析的终止时间戳.
        :return: list，截取后的异常metric列表.
        """
        result_list = []
        for metric in metric_list:
            start_index = metric.sample['timestamp'].index(start_timestamp)
            end_index = metric.sample['timestamp'].index(end_timestamp)

            metric.sample['timestamp'] = metric.sample['timestamp'][start_index:end_index]
            metric.sample['value'] = metric.sample['value'][start_index:end_index]

            temp_timestamp_list = ad_model.detect_anomaly(metric, 'single')

            if len(temp_timestamp_list) == 0:
                continue
            result_list.append(metric)

        return result_list
