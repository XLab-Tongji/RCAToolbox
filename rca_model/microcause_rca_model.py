import networkx as nx
import numpy as np
import pandas as pd
from pingouin import partial_corr
from matplotlib import pyplot as plt

from base.base_rca_model import BaseRCAModel
from utils.build_graph import build_graph_pcmci
from utils.ad_utils import ADUtils


class MicroCauseRCAModel(BaseRCAModel):
    """
    MicroCause根因检测模型
    """

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

    @staticmethod
    def get_Q_matrix(data, data_head, g, frontend, rho=0.2):
        """
        建立能为随机游走使用的关系依赖矩阵
        :param data: 原数据
        :param data_head: 数据头（service名字）
        :param g: 关系依赖图
        :param frontend: 开始节点
        :param rho: 参数
        :return:
        """
        corr = np.corrcoef(np.array(data).T)
        for i in range(corr.shape[0]):
            corr[i, i] = 0.0
        corr = np.abs(corr)

        Q = np.zeros([len(data_head), len(data_head)])
        for e in g.edges():
            Q[e[0], e[1]] = corr[frontend[0] - 1, e[1]]
            backward_e = (e[1], e[0])
            if backward_e not in g.edges():
                Q[e[1], e[0]] = rho * corr[frontend[0] - 1, e[0]]

        adj = nx.adj_matrix(g).todense()
        for i in range(len(data_head)):
            P_pc_max = None
            res_l = np.array([corr[frontend[0] - 1, k] for k in adj[:, i]])
            if corr[frontend[0] - 1, i] > np.max(res_l):
                Q[i, i] = corr[frontend[0] - 1, i] - np.max(res_l)
            else:
                Q[i, i] = 0
        l = []
        for i in np.sum(Q, axis=1):
            if i > 0:
                l.append(1.0 / i)
            else:
                l.append(0.0)
        l = np.diag(l)
        Q = np.dot(l, Q)
        return Q

    @staticmethod
    def get_Q_matrix_part_corr(data, data_head, g, frontend, rho=0.2):
        """
        建立能为随机游走使用的关系依赖矩阵
        :param data: 原数据
        :param data_head: 数据头（service名字）
        :param g: 关系依赖图
        :param frontend:开始节点
        :param rho:参数
        :return: 异常排名表
        """
        df = pd.DataFrame(data, columns=data_head)

        def get_part_corr(x, y):
            cond = get_confounders(y)
            if x in cond:
                cond.remove(x)
            if y in cond:
                cond.remove(y)
            ret = partial_corr(data=df,
                               x=df.columns[x], y=df.columns[y], covar=[df.columns[_] for _ in cond],
                               method='pearson')
            # For a valid transition probability, use absolute correlation values.
            return abs(float(ret.r))

        # Calculate the parent nodes set.
        pa_set = {}
        for e in g.edges():
            # Skip self links.
            if e[0] == e[1]:
                continue
            if e[1] not in pa_set:
                pa_set[e[1]] = set([e[0]])
            else:
                pa_set[e[1]].add(e[0])
        # Set an empty set for the nodes without parent nodes.
        for n in g.nodes():
            if n not in pa_set:
                pa_set[n] = set([])

        def get_confounders(j: int):
            ret = pa_set[frontend[0] - 1].difference([j])
            ret = ret.union(pa_set[j])
            return ret

        Q = np.zeros([len(data_head), len(data_head)])
        for e in g.edges():
            # Do not add self links.
            if e[0] == e[1]:
                continue
            # e[0] --> e[1]: cause --> result
            # Forward step.
            # Note for partial correlation, the two variables cannot be the same.
            if frontend[0] - 1 != e[0]:
                Q[e[1], e[0]] = get_part_corr(frontend[0] - 1, e[0])
            # Backward step
            backward_e = (e[1], e[0])
            # Note for partial correlation, the two variables cannot be the same.
            if backward_e not in g.edges() and frontend[0] - 1 != e[1]:
                Q[e[0], e[1]] = rho * get_part_corr(frontend[0] - 1, e[1])

        adj = nx.adj_matrix(g).todense()
        for i in range(len(data_head)):
            # Calculate P_pc^max
            P_pc_max = []
            # (k, i) in edges.
            for k in adj[:, i].nonzero()[0]:
                # Note for partial correlation, the two variables cannot be the same.
                if frontend[0] - 1 != k:
                    P_pc_max.append(get_part_corr(frontend[0] - 1, k))
            if len(P_pc_max) > 0:
                P_pc_max = np.max(P_pc_max)
            else:
                P_pc_max = 0

            # Note for partial correlation, the two variables cannot be the same.
            if frontend[0] - 1 != i:
                q_ii = get_part_corr(frontend[0] - 1, i)
                if q_ii > P_pc_max:
                    Q[i, i] = q_ii - P_pc_max
                else:
                    Q[i, i] = 0

        l = []
        for i in np.sum(Q, axis=1):
            if i > 0:
                l.append(1.0 / i)
            else:
                l.append(0.0)
        l = np.diag(l)
        Q = np.dot(l, Q)
        return Q

    def build(self, train_data, config):
        """
        样例异常检测（输入输出示例，并没有真正的异常检测）
        :param train_data: 训练数据，与base/base_data_loader.py中读入的train_data格式一致.
        :param config: 模型参数.
        :return 如果是每组实验一个模型，返回一个dict，key为experiment_id；如果是训练集整个是一个模型，返回该模型.
        """

        model = dict()
        for experiment_id, data in train_data['data'].items():
            # metric_data = data['metric']
            print(experiment_id)
            header, metric_sample_matrix = ADUtils.get_metric_data(data)
            matrix = ADUtils.get_martix(data)
            pcmci, pcmci_res = build_graph_pcmci(matrix, config['pc_alpha'], config['verbosity'])
            graph_without_weight = self.get_links(matrix, pcmci, pcmci_res, config['alpha_level'])
            pc_graph = self.get_Q_matrix_part_corr(matrix, header, graph_without_weight, config['frontend'],
                                                   config["rho"])

            # TODO:画关系图
            model[experiment_id] = {'pcmci': pcmci, 'pcici_res': pcmci_res,
                                    'graph_without_weight': graph_without_weight, 'header': header,
                                    'pc_graph': pc_graph,'entry': train_data['entry_metric_name'][experiment_id],
                                    'teleportation_prob': 0}

        return model
