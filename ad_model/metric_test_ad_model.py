from base.base_ad_model import BaseADModel


class MetricTestADModel(BaseADModel):
    """
    异常检测的一个模板.

    注：如需要根据构建异常检测模型，需要声明一个ad_model的类变量，通过anomaly_model_build方法构建.
    """

    def __init__(self):
        super().__init__()
        self.model = ''

    def detect_anomaly(self, data, mode, experiment_id, strip_correct_interval=True):
        """
        样例异常检测（输入输出示例，并没有真正的异常检测）

        :param data: dict，表征metric，与data_model/metric_data_model.py中的结构相同.
        :param mode: 异常检测模式，只检测第一个（取值为single）还是全部的（all）异常点.
        :param experiment_id: 实验信息，针对每一个实验中的相关数据分别载入构建好的异常检测模型.
        :param strip_correct_interval: 是否需要去除correct_interval中的部分（去掉正常部分）.
        :return list，元素为异常时间点对应的时间戳，如果list为空证明检测的数据是正常的.
        """
        result_dict = []

        if mode == 'single':
            result_dict.append(data.sample['timestamp'][0] + 300)
        elif mode == 'all':
            result_dict.append(data.sample['timestamp'][0] + 300)
            result_dict.append(data.sample['timestamp'][0] + 370)

        return result_dict

    def build_anomaly_model(self, data_loader):
        self.model = 'look look'

