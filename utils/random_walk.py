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


def firstorder_randomwalk(
        rca_model,
        rank_paces,
        start_node,
        teleportation_prob,
        label,
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
