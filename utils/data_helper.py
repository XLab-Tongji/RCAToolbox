import numpy as np


def linearly_interpolate_nans(data):
    """
    插值填补数字序列中的nan值

    :param data: np.array，包含nan值的原始数据.
    :return: np.array，插值后的数据
    """
    good = np.where(np.isfinite(data))
    if len(good[0]) == 0:
        return np.nan_to_num(data)
    mask = np.isnan(data)
    data[mask] = np.interp(np.flatnonzero(mask), np.flatnonzero(~mask), data[~mask])
    return data


def normalize(matrix, axis):
    """
    返回矩阵的归一化表示

    :param matrix: 原始矩阵
    :param axis: np.sum()参数，标识第axis个维度上的变化
    :return:
    """
    np.seterr(divide='ignore', invalid='ignore')
    matrix /= np.sum(matrix, axis=axis, keepdims=True, dtype=float)
    return np.nan_to_num(matrix)
