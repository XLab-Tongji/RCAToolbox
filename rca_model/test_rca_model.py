from base.base_rca_model import BaseRCAModel


class TestRCAModel(BaseRCAModel):
    """
    根因分析模型的一个模板.
    """

    def build(self, train_data, config):
        """
        样例异常检测（输入输出示例，并没有真正的异常检测）

        :param train_data: 训练数据，与base/base_data_loader.py中读入的train_data格式一致.
        :param config: 模型参数.
        :return 如果是每组实验一个模型，返回一个dict，key为experiment_id；如果是训练集整个是一个模型，返回该模型.
        """
        model = dict()

        for experiment_id, data in train_data.items():
            model[experiment_id] = 'a'

        return model
