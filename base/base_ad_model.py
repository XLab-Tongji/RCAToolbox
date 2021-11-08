from abc import ABC, abstractmethod


class BaseADModel(ABC):
    """
    异常检测(读取运维数据)的基类.
    """

    def __init__(self):
        pass

    @abstractmethod
    def detect_anomaly(self, data, mode):
        """
        根据算法的配置文件加载数据集，配置文件中的train、valid、test字段分别标识了不同种类的实验

        :param data: metric、tracing、logging间会有区别，metric为dict，与data_model/metric_data_model.py中的结构相同，tracing、logging为list.
        :param mode: 异常检测模式，只检测第一个（取值为single）还是全部的（all）异常点.
        :return list，元素为异常时间点对应的时间戳，如果list为空证明检测的数据是正常的.
        """
        raise NotImplementedError
