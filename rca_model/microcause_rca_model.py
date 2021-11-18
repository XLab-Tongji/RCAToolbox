import networkx as nx
import numpy as np

from matplotlib import pyplot as plt

from base.base_rca_model import BaseRCAModel
import tigramite.data_processing as pp
from tigramite.pcmci import PCMCI
from tigramite.independence_tests import ParCorr
from utils.ad_utils import ADUtils


class MicroCauseRCAModel(BaseRCAModel):
    """
    MicroCause模型
    """

    @staticmethod
    def get_metric_data(data):
        """

        :param data: DataLoader读出的所有数据
        :return: 二元元组，包括metric名称列表及数据二维矩阵
        """
        metric_data = data['metric']
        header = [metric_data[i].name for i in range(len(metric_data))]
        metric_sample_list = [metric_data[i].sample['value'] for i in range(len(metric_data))]
        metric_sample_matrix = np.array(metric_sample_list)
        idx = np.argwhere(np.all(metric_sample_matrix[..., :] == 0, axis=1))
        metric_sample_matrix = np.delete(metric_sample_matrix, idx, axis=0)
        header = np.delete(header, idx, axis=0)
        return header, metric_sample_matrix

    @staticmethod
    def run_pcmci(train_data, pc_alpha=0.1, verbosity=0):
        """
        跑改进的PC算法获得关系矩阵
        :param train_data: 原数据
        :param pc_alpha: 参数
        :param verbosity: 参数
        :return:
        """
        dataframe = pp.DataFrame(train_data)
        cond_ind_test = ParCorr()
        pcmci = PCMCI(dataframe=dataframe, cond_ind_test=cond_ind_test, verbosity=verbosity)
        pcmci_res = pcmci.run_pcmci(tau_max=10, pc_alpha=pc_alpha)
        return pcmci, pcmci_res

    @staticmethod
    def get_links(train_data, pcmci, results, alpha_level=0.01):
        """
        根据pc算法结果建立联系图
        :param train_data: 原数据
        :param pcmci:跑pc之后的结果
        :param results: pcmci_res
        :param alpha_level: 参数
        :return: 关系联系图（不带边权值）
        """
        pcmci_links = pcmci.return_significant_links(results['p_matrix'], results['val_matrix'],
                                                     alpha_level=alpha_level, include_lagzero_links=False)
        g = nx.DiGraph()
        for i in range(len(train_data)):
            g.add_node(i)
        for n, links in pcmci_links['link_dict'].items():
            for l in links:
                g.add_edge(n, l[0])
        return g

    def build(self, train_data, config):
        """
        样例异常检测（输入输出示例，并没有真正的异常检测）

        :param train_data: 训练数据，与base/base_data_loader.py中读入的train_data格式一致.
        :param config: 模型参数.
        :return 如果是每组实验一个模型，返回一个dict，key为experiment_id；如果是训练集整个是一个模型，返回该模型.
        """

        model = dict()
        for experiment_id, data in train_data.items():
            #metric_data = data['metric']
            header, metric_sample_matrix = self.get_metric_data(data)

            matrix = ADUtils.get_martix(data)
            pcmci, pcmci_res = self.run_pcmci(matrix, config['pc_alpha'], config['verbosity'])
            g = self.get_links(matrix, pcmci, pcmci_res, config['alpha_level'])
            plt.figure(figsize=config['figure_size'])
            nx.draw_networkx(g, pos=nx.circular_layout(g))
            model[experiment_id] = {'pcmci': pcmci, 'pcici_res': pcmci_res, 'graph': g, 'header': header}

        return model
