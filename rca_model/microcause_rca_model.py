from base.base_rca_model import BaseRCAModel


class MicroCauseRCAModel(BaseRCAModel):
    """
    MicroCause模型
    """

    def run_SPOT(data, q=1e-3, d=300, n_init=None):
        """
        跑SPOT算法

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
            # q: risk parameter
            # d: depth parameter
            s = dSPOT(q, d)  # DSPOT object
            s.fit(init_data, _data)  # data import
            s.initialize()  # initialization step
            results = s.run()  # run
            #     s.plot(results) 	 	# plot
            result_dict[svc_id] = results
        return result_dict

    def get_eta(SPOT_res, n_init):
        """
        获得潜在可能根因
        """
        eta = np.zeros([len(data_head)])
        ab_timepoint = [0 for i in range(len(data_head))]
        for svc_id in range(len(data_head)):
            mask = data[n_init:, svc_id] > np.array(SPOT_res[svc_id]['thresholds'])
            ratio = np.abs(data[n_init:, svc_id] - np.array(SPOT_res[svc_id]['thresholds'])) / np.array(
                SPOT_res[svc_id]['thresholds'])
            if mask.nonzero()[0].shape[0] > 0:
                eta[svc_id] = np.max(ratio[mask.nonzero()[0]])
                ab_timepoint[svc_id] = np.min(mask.nonzero()[0])
            else:
                eta[svc_id] = 0
        return eta, ab_timepoint

    def run_pcmci(pc_alpha=0.1, verbosity=0):
        """
        跑改进的PC算法获得关系矩阵
        """
        dataframe = pp.DataFrame(data)
        cond_ind_test = ParCorr()
        pcmci = PCMCI(dataframe=dataframe, cond_ind_test=cond_ind_test, verbosity=verbosity)
        pcmci_res = pcmci.run_pcmci(tau_max=10, pc_alpha=pc_alpha)
        # pcmci.print_significant_links(p_matrix=results['p_matrix'],
        #                                      val_matrix=results['val_matrix'],
        #                                      alpha_level=0.1)
        return pcmci, pcmci_res

    def get_links(pcmci, results, alpha_level=0.01):
        """
        根据pc算法结果建立联系图
        """
        pcmci_links = pcmci.return_significant_links(results['p_matrix'], results['val_matrix'],
                                                     alpha_level=alpha_level, include_lagzero_links=False)
        g = nx.DiGraph()
        for i in range(len(data_head)):
            g.add_node(i)
        for n, links in pcmci_links['link_dict'].items():
            for l in links:
                g.add_edge(n, l[0])
        return g

    def get_Q_matrix(g, rho=0.2):
        """
        建立能为随机游走使用的关系依赖矩阵
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

    def get_Q_matrix_part_corr(g, rho=0.2):
        """
        建立能为随机游走使用的关系依赖矩阵
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

    def build(self, train_data, config):
        """
        样例异常检测（输入输出示例，并没有真正的异常检测）

        :param train_data: 训练数据，与base/base_data_loader.py中读入的train_data格式一致.
        :param config: 模型参数.
        :return 如果是每组实验一个模型，返回一个dict，key为experiment_id；如果是训练集整个是一个模型，返回该模型.
        """
        # Data params
        # self.data_source = "real_micro_service"

        # Root trace params
        self.testrun_round = 1
        self.frontend = [14]
        self.true_root_cause = [6, 28, 30, 31]
        self.n_init = 1000

        # Debug params
        self.plot_figures = False
        self.verbose = False
        self.kws = {}


        cm = ConfigManager().update('notebook', {'limit_output': 100000})

        model = dict()
        for experiment_id, data in train_data.items():
            model[experiment_id] = 'a'

