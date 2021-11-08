from abc import ABC, abstractmethod


class BaseRunner(ABC):
    """
    runner(整合整个根因分析过程)的基类.

    Attributes:
        ad_model: 异常检测模型.
        rca_model: 根因分析模型，具体形式根据有监督、无监督方法存在不同，可能包含一个（训练集合起来一个）和多个模型（每次实验一个）.
        data_loader: base/base_data_loader.py中BaseDataLoader的派生类实例.
    """
    def __init__(self):
        self.data_loader = ''
        self.ad_model = ''
        self.rca_model = ''

    @abstractmethod
    def run(self):
        raise NotImplementedError

    @abstractmethod
    def test(self):
        raise NotImplementedError
