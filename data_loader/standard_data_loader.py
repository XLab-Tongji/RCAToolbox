import os
import json
from base.base_data_loader import BaseDataLoader


class StandardDataLoader(BaseDataLoader):
    """
    加载可观察数据数据集的标准类.

    Attributes:
        train_data: 有监督的训练数据，半监督/无监督下的基准数据（一般为正常数据）.
        valid_data: 数据源.
        test_data: 测试数据.
        三种数据具有相同的格式：
            {
                "experiment_id": {
                    "metric": []
                    "tracing": []
                    "logging": []
                    "label": []
                }
            }
        其中：
            experiment_id：某一次实验的标识符，一次实验一般对应一次混沌实验（制作的数据集）;
            - metric：此次实验的metric数据，其中包含的数据具体参见data_model/metric_data_model.py;
            - tracing：此次实验的tracing数据，其中包含的数据具体参见data_model/tracing_data_model.py;
            - logging：此次实验的logging数据，其中包含的数据具体参见data_model/logging_data_model.py;
            - label：此次实验的标签，目前设想一次实验中只有一个异常和一个根因，为了以后可能的扩展设计成列表.
        data_reader: 继承自base/base_data_reader的类实例，用于读取可观察数据.
        pre_processor: 继承自base/base_pre_processor的类实例，用于进行数据预处理.
    """

    def __init__(self, data_reader, pre_processor):
        super().__init__()
        # 为了注释不乱跳问题
        self.train_data = dict()
        self.valid_data = dict()
        self.test_data = dict()
        self.data_reader = data_reader
        self.pre_processor = pre_processor

    def load_data(self, rca_model_name, dataset):
        """
        根据算法的配置文件加载数据集，配置文件中的train、valid、test字段分别标识了不同种类的实验

        :param rca_model_name: str，采用的rca模型名称.
        :param dataset: str，数据集名称.
        :return 此对象，以供下一步异常检测使用
        """
        config_file_name = 'data_' + rca_model_name + '_' + dataset + '.json'
        config_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        config_path = os.path.join(os.path.join(config_path, 'config'), config_file_name)
        with open(config_path) as f:
            config_dict = json.load(f)

        type_config_dict = config_dict['data_type']
        for experiment_id in config_dict['train']:
            self.train_data[experiment_id] = self.load_single_experiment_data(dataset, experiment_id, type_config_dict)
        for experiment_id in config_dict['valid']:
            self.valid_data[experiment_id] = self.load_single_experiment_data(dataset, experiment_id, type_config_dict)
        for experiment_id in config_dict['test']:
            self.test_data[experiment_id] = self.load_single_experiment_data(dataset, experiment_id, type_config_dict)

        return self

    def load_single_experiment_data(self, dataset, experiment_id, type_config_dict):
        """
        根据配置文件中配置的数据类型，加载单组实验数据

        :param dataset: str，数据集名称.
        :param experiment_id: str，实验标识.
        :param type_config_dict: dict，对应加载的数据类型.
        :return dict，读取后的metric、tracing、logging数据.
        """
        result_dict = {
            'metric': dict(),
            'tracing': dict(),
            'logging': dict()
        }

        if type_config_dict['metric']:
            result_dict['metric'] = self.data_reader.metric_reader(dataset, experiment_id)
            result_dict['metric'] = self.pre_processor.metric_pre_processor(result_dict['metric'])
        if type_config_dict['tracing']:
            result_dict['tracing'] = self.data_reader.tracing_reader(dataset, experiment_id)
            result_dict['tracing'] = self.pre_processor.tracing_pre_processor(result_dict['tracing'])
        if type_config_dict['logging']:
            result_dict['logging'] = self.data_reader.logging_reader(dataset, experiment_id)
            result_dict['logging'] = self.pre_processor.logging_pre_processor(result_dict['logging'])
        result_dict['label'] = self.data_reader.label_reader(dataset, experiment_id)

        return result_dict
