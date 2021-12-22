import os
import json
import sys

from ad_model.n_sigma_ad_model import NSigmaADModel
from base.base_runner import BaseRunner
from data_reader.standard_data_reader import StandardDataReader
from data_loader.standard_data_loader import StandardDataLoader
from pre_processor.demo_pre_processor import DemoPreProcessor
from ad_model.spot_ad_model import SpotADModel
from utils.ad_utils import ADUtils
from rca_model.microcause_rca_model import MicroCauseRCAModel
from localization.random_walk_localization import RandomWalkLocalization
from notebook.services.config import ConfigManager
from utils.config_handler import config_loader


class MicroCauseRunner(BaseRunner):
    """
    MicroCause_runner(整合整个根因分析过程).

    Attributes:
        config_dict: 异常检测、根因分析、定位的参数配置.
    """

    def __init__(self):
        super().__init__()
        self.config_dict = config_loader('microcause_runner_config.json')
        self.spot_result_list = []

    @staticmethod
    def update_data(data):
        """
        将一行所有元素都相同或者有很长一段时间不动的数据的一整行都去掉，因为这一行的数据都没意义
        :param data: 传入的数据（字典）
        :return: 删好的数据
        """

        same_count = 0  # 检查一个service长时间不动的指标
        same_temp = 0
        for _, item in data.items():
            count = 0
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

        return data

    def run(self):
        # 构建data_loader
        standard_data_reader = StandardDataReader()
        demo_pre_processor = DemoPreProcessor()
        self.data_loader = StandardDataLoader(standard_data_reader, demo_pre_processor)
        self.data_loader.load_data(rca_model_name='rca_model_name', dataset='sock-shop')

        self.data_loader.train_data = self.update_data(self.data_loader.train_data)  # 删除无用数据列
        self.data_loader.valid_data = self.update_data(self.data_loader.valid_data)  # 删除无用数据列

        # 选取异常检测模型
        self.ad_model = NSigmaADModel()

        # 训练集异常检测与预处理
        self.data_loader.train_data = self.data_preparation(self.data_loader.train_data)

        # RCA模型搭建（有监督的根据训练数据搭建，无监督的训练集等于测试集，因此搭建的就是测试集的模型）
        microcause_rca_model = MicroCauseRCAModel()
        self.rca_model = microcause_rca_model.build(self.data_loader.train_data, self.config_dict['rca_model'])

        # 验证集异常检测与预处理
        # 无监督时不需要
        # self.data_loader.valid_data = self.data_merge(self.data_loader.train_data, self.spot_result_list)
        #
        # # 在验证集上进行根因定位测试
        # microcause_localization = RandomWalkLocalization()
        # # self.mergemodel(self.data_loader.valid_data,self.spot_result_list)
        # result_dict = microcause_localization.localize(rca_model=self.rca_model,
        #                                                data=self.data_loader.valid_data,
        #                                                config=self.config_dict['localization'])
        # print(result_dict)
        # TODO: 加入评价指标并将评价结果记录、输出

    def test(self):
        # 测试集异常检测与预处理
        self.data_loader.test_data = self.update_data(self.data_loader.test_data)  # 删除无用数据列
        self.data_loader.test_data = self.data_preparation(self.data_loader.test_data)
        # 在测试集上进行根因定位
        test_localization = RandomWalkLocalization(order=1)
        result_dict = test_localization.localize(rca_model=self.rca_model,
                                                 data=self.data_loader.test_data,
                                                 config=self.config_dict['localization'])
        base_dir = str(os.path.dirname(os.path.dirname(__file__))) + '/saved/model/microcause_runner/sock_shop_sigma/'
        filename = 'sock_shop_20210724_003000.json'#TODO 改名字
        with open(base_dir + filename, 'w') as json_file:
            json_file.write(json.dumps(result_dict))
        return result_dict

    def data_preparation(self, raw_data):
        """
        训练集、验证集、测试集可能需要统一地处理，归类到这里.
        :param raw_data: 训练集、验证集或测试集数据.
        :return: dict，处理好的数据.
        """
        result_dict = {
            'data': dict(),
            'entry_metric_name': dict()
        }

        for experiment_id, data in raw_data.items():

            forward_interval = self.config_dict['ad_model']['forward_interval']
            backward_interval = self.config_dict['ad_model']['backward_interval']

            for metric in data['metric']:

                self.ad_model.build_anomaly_model(metric, experiment_id)

            detect_metric_list = []
            for metric in data['metric']:
                if ('service' in metric.name and 'qps' in metric.name) or (
                        'node' in metric.name and 'System Load' in metric.name):
                    detect_metric_list.append(metric)
            first_timestamp_info = ADUtils.ad_metric_find_first_timestamp(ad_model=self.ad_model,
                                                                          metric_list=detect_metric_list,
                                                                          experiment_id=experiment_id)

            first_timestamp = ''
            if len(first_timestamp_info) > 0:
                first_timestamp = first_timestamp_info[0][0]
                result_dict['entry_metric_name'][experiment_id] = first_timestamp_info[0][1]
            else:
                # TODO: 日志记录下这里存在问题
                print('No anomaly timestamp detected!: ', experiment_id)
                raw_data[experiment_id]['metric'] = []
                continue
                ...
            filtered_data = ADUtils.ad_metric_filter(ad_model=self.ad_model,
                                                     metric_list=data['metric'],
                                                     start_timestamp=first_timestamp - forward_interval,
                                                     end_timestamp=first_timestamp + backward_interval,
                                                     experiment_id=experiment_id)
            raw_data[experiment_id]['metric'] = filtered_data
        result_dict['data'] = raw_data
        return result_dict

    def evaluation(self):
        pass

    def findmin(self,list):
        """
        找除0以外外最小值
        Args:
            list: 列表

        Returns:
            最小值
        """
        min=999999
        for i in range(len(list)):
            if list[i]!=0 and list[i]<min:
                min=list[i]
        return min


if __name__ == '__main__':
    microcause_runner = MicroCauseRunner()
    microcause_runner.run()
    final_result = microcause_runner.test()
    ...
