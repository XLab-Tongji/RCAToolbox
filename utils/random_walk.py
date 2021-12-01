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
        rca_model,
        epoches,
        start_node,
        teleportation_prob,
        walk_step=1000,
        print_trace=False,
):
    """
              根据训练集中的数据构建根因分析模型.
              :param rca_model: 构建好的根因分析模型,传入的应该是一个类似于矩阵的变量
              :param epoches: 迭代次数
              :param start_node:游走开始节点
              :param teleportation_prob:当算法陷入出度为0的节点，依照概率跳转到其他节点。
              :param walk_step:游走步长
              :param print_trace:是否打印轨迹
              :return dict，每组实验定位的结果，key为experiment_id，value类型为list，其中的每个元素为元组，第一个维度标识根因，第二个维度标识可能性（或评判可能性的依据），按可能性由大到小排列.
            """
    label = [i for i in range(len(rca_model))]
    n = rca_model.shape[0]
    score = np.zeros([n])
    current = start_node - 1
    for epoch in range(epoches):
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


def second_order_random_walk(header, edge_trans_prob, epochs, front_end, steps):
    """
    二阶随机游走算法

    :param header: 数据头，即服务名
    :param edge_trans_prob: 边转移概率矩阵
    :param epochs: 轮数
    :param front_end: 前端节点
    :param steps: 单轮随机游走步数
    :return: 相关性得分列表，按分数降序排列
    """
    n = edge_trans_prob.shape[0]
    score = np.zeros([n])
    for epoch in range(epochs):
        previous = front_end
        current = front_end
        for step in range(steps):
            if np.sum(edge_trans_prob[previous, current]) == 0:
                break
            next_node = np.random.choice(range(n), p=edge_trans_prob[previous, current])
            score[next_node] += 1
            previous = current
            current = next_node
    score_list = list(zip(header, score))

    # 排序 并排除score为0的项
    score_list.sort(key=lambda x: x[1], reverse=True)
    for index, pair in enumerate(score_list):
        if pair[1] == 0:
            score_list = score_list[0:index]
            break
    return score_list

