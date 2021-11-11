from base.base_ad_model import BaseADModel


class SpotADModel(BaseADModel):
    """
    spot检测

    """

    def __init__(self):
        super().__init__()
        self.model = ''

    def detect_anomaly(self, data, mode):
        """
        样例异常检测（输入输出示例，并没有真正的异常检测）

        :param data: dict，表征metric，与data_model/metric_data_model.py中的结构相同.
        :param mode: 异常检测模式，只检测第一个（取值为single）还是全部的（all）异常点.
        :return list，元素为异常时间点对应的时间戳，如果list为空证明检测的数据是正常的.
        """
        result_dict = []

        if mode == 'single':
            result_dict.append(data.sample['timestamp'][0] + 300)
        elif mode == 'all':
            result_dict.append(data.sample['timestamp'][0] + 300)
            result_dict.append(data.sample['timestamp'][0] + 370)

        return result_dict

    def run_SPOT(data, q=1e-3, d=300, n_init=None):
        """
        :param q: 风险参数
        :param d: 深度参数
        :param n_init: 中间截断位置
        :return:
        """
        result_dict = {}
        if n_init is None:
            n_init = int(0.5 * len(data))
        for svc_id in range(len(data_head)):
            print("{:-^40}".format("svc_id: {}".format(svc_id)))
            init_data = data[:n_init, svc_id]  # initial batch
            _data = data[n_init:, svc_id]  # stream

            s = dSPOT(q, d)  # DSPOT object
            s.fit(init_data, _data)  # data import
            s.initialize()  # initialization step
            results = s.run()  # run
            #     s.plot(results) 	 	# plot
            result_dict[svc_id] = results
        return result_dict


    def build_anomaly_model(self, data_loader):
        self.model = 'spot'

