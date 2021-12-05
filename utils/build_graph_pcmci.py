from tigramite.independence_tests import ParCorr
from tigramite.pcmci import PCMCI
import tigramite.data_processing as pp


def build_graph_pcmci(train_data, pc_alpha=0.1, verbosity=0):
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
