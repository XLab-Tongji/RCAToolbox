import os
import json


def config_loader(config_file_name):
    """
    加载配置文件

    :param config_file_name: 配置文件名.
    :return: dict，加载后的配置文件信息.
    """
    config_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    config_path = os.path.join(os.path.join(config_path, 'config'), config_file_name)
    with open(config_path) as f:
        config_dict = json.load(f)
    return config_dict
