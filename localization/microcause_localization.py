import networkx as nx
import numpy as np
import pandas as pd
from pingouin import partial_corr
from utils.ad_utils import ADUtils
from base.base_localization import BaseLocalization


def change_label(vis_list, data):
    """
    将vis_list里的label改为service的名字
    :param vis_list: 更改之前的list
    :param data: 原始数据
    :return: 更改好后的vis_list
    """
    temp = []
    for item in vis_list:
        name = data['metric'][item].name
        temp.append(name)

    return temp


class MicroCauseLocalization(BaseLocalization):
    """
    MicroCause的根因定位
    """

    @staticmethod
    def microcause_random_walk(
            data,
            P,
            epochs,
            start_node,
            teleportation_prob,
            walk_step=50,
            print_trace=False,
    ):
        """
        随机游走算法
        :param data:元数据
        :param P: 关系矩阵.
        :param epochs: 代数.
        :param start_node:开始节点.
        :param teleportation_prob:转移的概率
        :param walk_step:每一代走的步数
        :param print_trace:是否打印轨迹
        :return dict，每组实验定位的结果，key为experiment_id，value类型为list，其中的每个元素为元组，第一个维度标识根因，第二个维度标识可能性（或评判可能性的依据），按可能性由大到小排列.

        """

        n = P.shape[0]
        score = np.zeros([n])
        current = start_node - 1
        for epoch in range(epochs):
            current = start_node - 1
            if print_trace:
                print("\n{:2d}".format(current + 1), end="->")
            for step in range(walk_step):
                if np.sum(P[current]) == 0:
                    break
                else:
                    next_node = np.random.choice(range(n), p=P[current])
                    if print_trace:
                        print("{:2d}".format(current + 1), end="->")
                    score[next_node] += 1
                    current = next_node
        label = [i for i in range(n)]
        label = change_label(label, data)
        score_list = list(zip(label, score))
        score_list.sort(key=lambda x: x[1], reverse=True)
        return score_list

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

    def localize(self, rca_model, data, config):
        """
        根据训练集中的数据构建根因分析模型.

        :param rca_model: 构建好的根因分析模型.
        :param data: 验证集或测试集数据，与base/base_data_loader.py中读入的valid_data、test_data格式一致.
        :param config: 模型参数.
        :return dict，每组实验定位的结果，key为experiment_id，value类型为list，其中的每个元素为元组，第一个维度标识根因，第二个维度标识可能性（或评判可能性的依据），按可能性由大到小排列.
        """
        result_dict = dict()
        for experiment_id, data in data.items():
            model = rca_model[experiment_id]
            matrix = ADUtils.get_martix(data)
            Q = self.get_Q_matrix_part_corr(matrix, model['header'], model['graph'], config['frontend'], config["rho"])
            vis_list = self.microcause_random_walk(data, Q, 1000, config['frontend'][0], config["teleportation_prob"],
                                                   config["walk_step"])


            result_dict[experiment_id] = vis_list

        return result_dict
