import os
import json
import sys

sys.path.append('../')
from base.base_runner import BaseRunner
from data_reader.standard_data_reader import StandardDataReader
from data_loader.standard_data_loader import StandardDataLoader
from pre_processor.demo_pre_processor import DemoPreProcessor
from ad_model.spot_ad_model import SpotADModel
from utils.ad_utils import ADUtils
from rca_model.microcause_rca_model import MicroCauseRCAModel
from localization.microcause_localization import MicroCauseLocalization
from notebook.services.config import ConfigManager


class MicroCauseRunner(BaseRunner):
    """
    MicroCause_runner(整合整个根因分析过程).

    Attributes:
        config_dict: 异常检测、根因分析、定位的参数配置.
    """

    def __init__(self):
        super().__init__()
        self.config_dict = dict()
        self.config_loader()
        self.spot_result_list = []

    @staticmethod
    def update_data(train_data):
        """
        将一行所有元素都相同或者有很长一段时间不动的数据的一整行都去掉，因为这一行的数据都没意义
        :param train_data: 传入的数据
        :return: 删好的数据
        """
        count = 0
        same_count = 0  # 检查一个service长时间不动的指标
        same_temp = 0
        for _, item in train_data.items():
            for i in range(len(item['metric'])):
                i = i - count
                temp = item['metric'][i].sample['value'][0]
                same_temp = temp
                flag = 0
                for value in item['metric'][i].sample['value']:
                    if value != temp:
                        flag = 1
                    if value != same_temp:
                        same_count = 0
                        same_temp = value
                    elif value == same_temp:
                        same_count += 1
                        if same_count >= 150:
                            same_count = 0
                            flag = 0
                            break
                if flag == 0:
                    item['metric'].remove(item['metric'][i])
                    count += 1

        return train_data

    def run(self):
        # 构建data_loader
        standard_data_reader = StandardDataReader()
        demo_pre_processor = DemoPreProcessor()
        self.data_loader = StandardDataLoader(standard_data_reader, demo_pre_processor)
        self.data_loader.load_data(rca_model_name='rca_model_name', dataset='demo')

        self.data_loader.train_data = self.update_data(self.data_loader.train_data)  # 删除无用数据列
        self.data_loader.valid_data = self.update_data(self.data_loader.valid_data)  # 删除无用数据列

        # 选取异常检测模型
        self.ad_model = SpotADModel()

        # 训练集异常检测与预处理
        self.spot_result_list = self.data_preparation(self.data_loader.train_data, self.ad_model)

        # RCA模型搭建（有监督的根据训练数据搭建，无监督的训练集等于测试集，因此搭建的就是测试集的模型）
        microcause_rca_model = MicroCauseRCAModel()
        self.rca_model = microcause_rca_model.build(self.data_loader.train_data, self.config_dict['rca_model'])

        # 验证集异常检测与预处理

        # self.data_loader.valid_data = self.data_merge(self.data_loader.train_data, self.spot_result_list)

        # 在验证集上进行根因定位测试
        microcause_localization = MicroCauseLocalization()
        # self.mergemodel(self.data_loader.valid_data,self.spot_result_list)
        result_dict = microcause_localization.localize(rca_model=self.rca_model,
                                                       data=self.data_loader.train_data,
                                                       config=self.config_dict['localization'])
        print(result_dict)
        # TODO: 加入评价指标并将评价结果记录、输出

    def test(self):
        # 测试集异常检测与预处理
        self.data_loader.test_data = self.update_data(self.data_loader.test_data)  # 删除无用数据列
        self.data_loader.test_data = self.data_preparation(self.data_loader.test_data, self.ad_model)
        # 在测试集上进行根因定位
        test_localization = MicroCauseLocalization()
        result_dict = test_localization.localize(rca_model=self.rca_model,
                                                 data=self.data_loader.test_data,
                                                 config=self.config_dict['localization'])
        return result_dict

    def data_preparation(self, train_data, ad_model):
        """
        训练集、验证集、测试集可能需要统一地处理，归类到这里.
        :param train_data: 训练集、验证集或测试集数据.
        :param ad_model: 异常检测模型.
        :return: dict，处理好的数据.(这里是跑完spot后的eta和ab_timepoint)
        """
        model = []
        for experiment_id, data in train_data.items():
            matrix = ADUtils.get_martix(data)
            model.append(ad_model.build_anomaly_model(matrix))
        return model

    def config_loader(self):
        """
        加载配置文件
        """
        config_file_name = 'microcause_runner_config.json'
        config_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        config_path = os.path.join(os.path.join(config_path, 'config'), config_file_name)
        with open(config_path) as f:
            config_dict = json.load(f)
        self.config_dict = config_dict

    def evaluation(self):
        pass


if __name__ == '__main__':
    microcause_runner = MicroCauseRunner()
    microcause_runner.run()
    final_result = microcause_runner.test()
    ...
