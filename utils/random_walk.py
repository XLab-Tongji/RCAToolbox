import numpy as np


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


def first_order_random_walk(
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
        # if print_trace:
        # print("\n{:2d}".format(current + 1), end="->")
        # TODO：输出路径
        for step in range(walk_step):
            if np.sum(P[current]) == 0:
                break
            else:
                next_node = np.random.choice(range(n), p=P[current])
                # if print_trace:
                #     print("{:2d}".format(current + 1), end="->")
                # TODO：输出路径
                score[next_node] += 1
                current = next_node
    label = [i for i in range(n)]
    label = change_label(label, data)
    score_list = list(zip(label, score))
    score_list.sort(key=lambda x: x[1], reverse=True)
    return score_list
