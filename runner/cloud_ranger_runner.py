from base.base_runner import BaseRunner
from data_reader.standard_data_reader import StandardDataReader
from data_loader.standard_data_loader import StandardDataLoader
from pre_processor.demo_pre_processor import DemoPreProcessor
from ad_model.metric_test_ad_model import MetricTestADModel
from utils.ad_utils import ADUtils
from rca_model.cloud_ranger_rca_model import CloudRangerModel
from localization.random_walk_localization import RandomWalkLocalization
import os
import json
from utils.config_handler import config_loader


class CloudRangerRunner(BaseRunner):
    """
    CloudRanger框架runner(整合整个根因分析过程).

    Attributes:
        config_dict: 异常检测、根因分析、定位的参数配置.
    """

    def __init__(self):
        super().__init__()
        self.config_dict = config_loader('cloud_ranger_runner_config.json')

    def run(self):
        # 构建data_loader
        standard_data_reader = StandardDataReader()
        demo_pre_processor = DemoPreProcessor()
        self.data_loader = StandardDataLoader(standard_data_reader, demo_pre_processor)
        self.data_loader.load_data(rca_model_name='rca_model_name', dataset='demo')

        # 选取异常检测模型
        self.ad_model = MetricTestADModel()

        # 训练集异常检测与预处理
        self.data_loader.train_data = self.data_preparation(self.data_loader.train_data, self.ad_model)

        # RCA模型搭建（有监督的根据训练数据搭建，无监督的训练集等于测试集，因此搭建的就是测试集的模型）
        cloud_ranger_rca_model = CloudRangerModel()
        self.rca_model = cloud_ranger_rca_model.build(self.data_loader.train_data, self.config_dict['rca_model'])

        # 验证集异常检测与预处理
        self.data_loader.valid_data = self.data_preparation(self.data_loader.valid_data, self.ad_model)
        # 在验证集上进行根因定位测试
        cloud_ranger_localization = RandomWalkLocalization(order=2)
        result_dict = cloud_ranger_localization.localize(rca_model=self.rca_model,
                                                         data=self.data_loader.valid_data,
                                                         config=self.config_dict['localization'])

        print('Results on validation set:', result_dict)

    def test(self):
        # 测试集异常检测与预处理
        self.data_loader.test_data = self.data_preparation(self.data_loader.test_data, self.ad_model)
        # 在测试集上进行根因定位
        cloud_ranger_localization = RandomWalkLocalization(order=2)
        result_dict = cloud_ranger_localization.localize(rca_model=self.rca_model,
                                                         data=self.data_loader.test_data,
                                                         config=self.config_dict['localization'])
        print('Results on test set:', result_dict)
        return result_dict

    def data_preparation(self, raw_data, ad_model):
        """
        训练集、验证集、测试集可能需要统一地处理，归类到这里.
        :param raw_data: 训练集、验证集或测试集数据.
        :param ad_model: 异常检测模型.
        :return: dict，处理好的数据.
        """
        for experiment_id, data in raw_data.items():
            forward_interval = self.config_dict['ad_model']['forward_interval']
            backward_interval = self.config_dict['ad_model']['backward_interval']

            first_timestamp = ADUtils.ad_metric_find_first_timestamp(ad_model=ad_model,
                                                                     metric_list=data['metric'])
            if len(first_timestamp) > 0:
                first_timestamp = first_timestamp[0]
            else:
                # TODO: 日志记录下这里存在问题
                ...
            filtered_data = ADUtils.ad_metric_filter(ad_model=ad_model,
                                                     metric_list=data['metric'],
                                                     start_timestamp=first_timestamp - forward_interval,
                                                     end_timestamp=first_timestamp + backward_interval)
            raw_data[experiment_id]['metric'] = filtered_data
        return raw_data

    def evaluation(self):
        pass


if __name__ == '__main__':
    cloud_ranger_runner = CloudRangerRunner()
    cloud_ranger_runner.run()
    final_result = cloud_ranger_runner.test()
    ...
