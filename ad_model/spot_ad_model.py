from base.base_ad_model import BaseADModel
import numpy as np
from utils.spot import dSPOT


class SpotADModel(BaseADModel):
    """
    spot检测

    """

    def __init__(self):
        super().__init__()
        self.model = ''

    def detect_anomaly(self, data, mode, experiment_id, strip_correct_interval=True):
        """
        样例异常检测
        :param data: dict，表征metric，与data_model/metric_data_model.py中的结构相同.
        :param mode: 异常检测模式，只检测第一个（取值为single）还是全部的（all）异常点.
        :param experiment_id: 实验信息，针对每一个实验中的相关数据分别载入构建好的异常检测模型.
        :param strip_correct_interval: 是否需要去除correct_interval中的部分（去掉正常部分）.
        :return list，元素为异常时间点对应的时间戳，如果list为空证明检测的数据是正常的.
        """
        result_dict = []

        if mode == 'single':
            # result_dict.append(data.sample['timestamp'][0] + 300)
            result_dict = self.build_anomaly_model(data)

        elif mode == 'all':
            result_dict.append(data.sample['timestamp'][0] + 300)
            result_dict.append(data.sample['timestamp'][0] + 370)
            # all的build_anomaly_model还没写

        return result_dict

    @staticmethod
    def run_spot(data, q=1e-3, d=200, n_init=None):
        """
        跑spot
        :param data: 读取到的数据
        :param q: 风险参数
        :param d: 深度参数
        :param n_init: 中间截断位置
        :return: result列表，跑SPOT之后，每个度量的时间序列
        """
        result_dict = {}
        if n_init is None:
            n_init = int(0.5 * len(data))
        for svc_id in range(len(data[0])):
            # print("{:-^40}".format("svc_id: {}".format(svc_id)))
            # TODO: 输出service头

            init_data = data[:n_init, svc_id]  # initial batch
            _data = data[n_init:, svc_id]  # stream

            s = dSPOT(q, d)  # dSPOT object
            s.fit(init_data, _data)  # data import
            s.initialize()  # initialization step
            results = s.run()  # run
            #     s.plot(results) 	 	# plot
            result_dict[svc_id] = results
        return result_dict

    @staticmethod
    def get_eta(data, spot_res, n_init):
        """
        获得潜在可能根因
        :param data: 读取到的数据
        :param spot_res: 跑完spot之后的得到的结果
        :param n_init: 中间截断位置
        :return: eta,每个度量的异常水平；ab_timepoint异常发生时间，都是list
        """
        eta = np.zeros([len(data[0])])
        ab_timepoint = [0 for i in range(len(data[0]))]
        for svc_id in range(len(data[0])):
            mask = data[n_init:, svc_id] > np.array(spot_res[svc_id]['thresholds'])
            ratio = np.abs(data[n_init:, svc_id] - np.array(spot_res[svc_id]['thresholds'])) / np.array(
                spot_res[svc_id]['thresholds'])
            if mask.nonzero()[0].shape[0] > 0:
                eta[svc_id] = np.max(ratio[mask.nonzero()[0]])
                ab_timepoint[svc_id] = np.min(mask.nonzero()[0])
            else:
                eta[svc_id] = 0
        return eta, ab_timepoint

    def build_anomaly_model(self, data):
        """
        建立异常模型
        :param data: 原数据
        :return: 含有eta和ab_timepoint的字典
        """

        self.model = 'spot'
        spot_result = {}
        spot_res = self.run_spot(data, q=1e-3, d=150)
        eta, ab_timepoint = self.get_eta(data, spot_res, int(0.5 * len(data)))

        # for i in range(len(data[0])):
        #     print(f"{i + 1:<2}: {eta[i]:>6.2f}")
        # TODO:输出各个service的异常分数

        spot_result['eta'] = eta
        spot_result['ab_timepoint'] = ab_timepoint
        return spot_result
