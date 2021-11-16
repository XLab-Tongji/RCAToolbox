import math

import numpy as np


def calc_pearson(matrix, method='default', zero_diag=True):
    """Calculate the pearson correlation between nodes

    Params:
        matrix: data of shape [N, T], N is node num, T is sample num
        method: method used, default for manually calculation,
            numpy for numpy implementation
        zero_diag:
                if zero the self correlation value (in diagonal position)
    """

    # 一行是一个数据
    if method == 'numpy':
        res = np.corrcoef(np.array(matrix))
        if zero_diag:
            for i in range(res.shape[0]):
                res[i, i] = 0.0
        res = res.tolist()
    else:
        nrows = len(matrix)
        ncols = len(matrix[0])
        n = ncols * 1.0
        res = [[0 for _ in range(nrows)] for _ in range(nrows)]
        for i in range(nrows):
            idx = i + 1
            for j in range(idx, nrows):
                a = b = c = f = e = 0
                for k in range(0, ncols):
                    a += matrix[i][k] * matrix[j][k]  # sigma xy
                    b += matrix[i][k]  # sigma x
                    c += matrix[j][k]  # sigma y
                    e += matrix[i][k] * matrix[i][k]  # sigma xx
                    f += matrix[j][k] * matrix[j][k]  # sigma yy

                para1 = a
                para2 = b * c / n
                para3 = e
                para4 = b * b / n
                para5 = f
                para6 = c * c / n

                r1 = para1 - para2
                r2 = (para3 - para4) * (para5 - para6)
                r2 = math.sqrt(r2)
                r = 1.0 * r1 / r2
                res[i][j] = res[j][i] = r * 1.00000
        if not zero_diag:
            for i in range(nrows):
                for j in range(nrows):
                    res[i][j] = 1.0
    return res
