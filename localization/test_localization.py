import numpy as np

from base.base_localization import BaseLocalization


class TestLocalization(BaseLocalization):
    """
    定位的一个模板.
    """

    def firstorder_randomwalk(
            self,
            rca_model,
            rank_paces,
            start_node,
            teleportation_prob,
            label=[],
            walk_step=1000,
            print_trace=False,
    ):
        n = rca_model.shape[0]
        score = np.zeros([n])
        current = start_node - 1
        for epoch in range(rank_paces):
            if print_trace:
                print("\n{:2d}".format(current + 1), end="->")
            for step in range(walk_step):
                if np.sum(rca_model[current]) == 0:
                    current = np.random.choice(range(n), p=teleportation_prob)
                    break
                else:
                    next_node = np.random.choice(range(n), p=rca_model[current])
                    if print_trace:
                        print("{:2d}".format(current + 1), end="->")
                    score[next_node] += 1
                    current = next_node
        score_list = list(zip(label, score))
        score_list.sort(key=lambda x: x[1], reverse=True)
        return score_list

    def localize(self, rca_model, rank_paces, fronted, teleportation_prob, label):
        """
        根据训练集中的数据构建根因分析模型.
        :param rca_model: 构建好的根因分析模型.
        :param rank_paces:游走步长
        :param fronted:前端服务
        :param teleportation_prob:前端服务转移概率
        :param label:服务编号
        :return list:单组实验定位结果,第一个维度标识根因，第二个维度标识可能性（或评判可能性的依据），按可能性由大到小排列.
        """
        return  self.firstorder_randomwalk(
            rca_model,
            rank_paces,
            fronted,
            teleportation_prob,
            label=[],
            walk_step=1000,
            print_trace=False,
    )
