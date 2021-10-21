Root Cause Detection in a Service-Oriented Architecture

论文阅读整理与归纳

### 问题引入：

大型网站主要是作为面向服务的体系结构来构建的。 在这里，服务是专门针对某一任务的，在多台机器上运行，并相互通信以服务于用户的请求。 在此通信期间，一个服务度量的异常变化可能传播到其他服务，从而导致请求的总体退化。 由于任何这种退化都对收入产生影响，维护正确的功能是最重要的：必须尽快找到任何异常的根本原因。 这是具有挑战性的，因为对于给定的服务有许多度量或传感器，而现代网站通常由数百个服务组成，在多个数据中心的数千台机 器上运行。

### 解决方案：

本文介绍了Monitor Rank算法，它可以减少在这种面向服务的体系结构中寻找异常根源所需的时间、领域知识和人力。 在异常情况下，Monitor Rank提供了一个可能的根本原因的排序列表，供监察组调查。 monitorRank算法使用每个传感器的历史和当前时间序列度量，以及传感器之间生成的调用图作为输入，输出是一个可能的异常的根源有序序列（评分依据是root cause score）。

（调用图需要包含外部因素，而不能仅使用基本调用图）

该算法是一个非机器学习的算法（不需要训练）

![截屏2021-10-20 下午9.39.04.png](https://img-youpai.weixiaoi.com/tu/2021/1020/1634744565211020.png)

首先度量收集系统接收和聚合来自所有传感器的度量， （提取kafka系统中的数据，缓冲并聚合到更粗的时间粒度，然后存储到一个时间分区数据库中。）

来自Kafka的度量数据也被批处理系统Hadoop消耗，并存储Hadoop 分布式文件系统(HDFS)上)。 定期调度的Hadoop 作业以度量数据的快照作为输入，并输出调用图和外部因 素。

#### 调用图形生成：

存储在Hadoop上的每个度量数据点都包含由前端传感器引入的唯一通用标识符，然后沿着调用链传递。 度量数据点还包含调用者和callee传感器名称。 Hadoop作业加入通用id上的快照度量数据，然后结合单个传感器名称生成调用图。（基本调用图无法展现外部因素影响）

#### 提取外部因素：

首先使用了文献中的一个检测算法检测出一个异常的前端传感器相应的异常度量和时间区间。对该算法输出的每一个异常（这里称之为伪异常），需要计算相应的度量数据与所有其他传感器的相关性。

如何测定相关性：pattern similarity

如果我们研究伪异常时刻传感器之间的度量模式相似性，并找到一组通常表现出高模式相似性的传感器，那么我们可以假设一些外部因素的影响。

### 实时引擎：

当度量收集管道和批处理模式引擎在后台间断性运行时，实时引擎负责为来自监控团队的查询提供服务。 一个简单的用户界面允许他们输入一个前端传感器，一个度量，以及与观察到的异常对应的时间段。 结果是一个有序的根原因传感器列表。 用户界面的交互性质允许团队不断地改变他们的输入，同时在接近实时的情况下返回诊断指南。

虽然度量模式相似性评分对于检测传感器与给定异常的相关性是有用的，但相关性不意味着因果关系。这些结果对被视为候选，需要进一步添加调用图来更好地对候选集进行排序。

#### 随机游走算法：

输入：一个调用图，以及一个异常前端传感器节点vfe和每个传感器vi∈V的模式相似度评分Si。

为方便起见，所有传感器的相似度评分记为向量S = [S1，···，S|V |]∈(0,1]|V |。为使随机walker按模式相似度评分Si的比例访问每个节点vi，将每条边eij的强度赋值为Sj。

#### 添加自边：

具体来说，对于每个节点v，对应的自边e的强度等于相似度评分S减去子节点的最大相似度评分，通过这种方式，随机步行者被鼓励移动到相似度高的节点，但避免落入与给定异常无关的节点。作为一个例外，我们没有向前端节点添加自边，即e11 = 0，因为随机漫步者不需要停留在v1。

#### 添加回边：

当随机步行者落入与给定异常不相关的节点时，就没有办法逃脱，直到下一次瞬间移动。由于调用图中某条边的方向趋向于从前端到后端，随机步行者很可能自然地被困在调用图的分支中。在图4中，假设在前端传感器v1上观察到一个异常，节点v2是唯一与给定异常相关的传感器。对于给定的异常，节点v2的模式相似度评分甚至高于其他节点v3 ~ v7。如果节点v3 ~ v7的模式相似度得分不可忽略，则随机walker就会落入图4(节点v3 ~ v7)中后代的右侧。在这种情况下，无论节点与给定的异常有多么无关，随机步行者将停留在节点v3 ~ v7上，直到下一次随机瞬移发生。

·每个后向边的强度设置都小于到达同一节点的真边的强度设置。（pSi）

·如果ρ的价值高,随机沃克更受限制的路径调用图,也就是说,从上游到下游。另一方面，当ρ值较低时，随机步行者以更大的灵活性探索节点。

·如果调用图表示传感器之间的一个真正的依赖图，我们将设置ρ较高

代码：

```
    if verbose:
        # 打印方法名
        print("{:#^80}".format("Monitor Rank"))
        if verbose>=3:
            # 打印方法变量
            print("{:-^80}".format(data_source))
            print("{:^10}pc aggregate  :{}".format("", pc_aggregate))
            print("{:^10}pc alpha      :{}".format("", pc_alpha))
            print("{:^10}rho           :{}".format("", rho))
    # 加载数据
    # Use raw_data, data_head if it is provided in kws
    if 'data' not in kws:
        data, data_head = load(
            os.path.join("data", data_source, "rawdata.xlsx"),
            normalize=True,
            zero_fill_method='prevlatter',
            aggre_delta=pc_aggregate,
            verbose=verbose,
        )
        # Transpose data to shape [N, T]
        data = data.T
    else:
        data_head = kws['data_head']
        # raw_data is of shape [T, N]. Here we first transpose it to [N, T] and then aggregate.
        raw_data = kws['data']
        data = np.array([aggregate(row, pc_aggregate) for row in raw_data.T])

    rela = calc_pearson(data, method="numpy", zero_diag=False)
    
    # region Build call graph from file or PC algorithm or parameters in kws
    
    # The file name for saving dependency graph
    window_start=0
    if 'window_start' in kws:
        window_start=kws['window_start']
    dep_graph_filepath = os.path.join(
        "monitor_rank",
        "results",
        data_source,
        "dep_graph_agg{}_alpha{}_winstart{}_len{}.xlsx".format(pc_aggregate, pc_alpha, window_start, data.shape[1]),
    )
    
    # When PC dep_graph isn't given, use PC algorithm
    if 'dep_graph' not in kws:
        if data_source == "pymicro":
            # Real call topology matrix
            dep_graph = readExl(os.path.join("data", data_source, "true_callgraph.xlsx"))
        elif data_source == "real_micro_service":
            # If it is not in runtime_debug mode, save and load previous constructed graph if possible
            if os.path.exists(dep_graph_filepath) and not runtime_debug:
                # If previous dependency graph exists, load it.
                if verbose and verbose >= 2:
                    # verbose level >= 2: print dependency graph loading info
                    print(
                        "{:^10}Loading existing link matrix file: {}".format(
                            "", dep_graph_filepath
                        )
                    )
                dep_graph = readExl(dep_graph_filepath)
            else:
                # If previous dependency graph doesn't exist, genereate it using PC algorithm.
                if verbose and verbose >= 2:
                    # verbose level >= 2: print dependency graph construction info
                    print("{:^10}Generating new link matrix".format(""))
                dep_graph = build_graph_pc(data, alpha=pc_alpha)
    # When PC dep_graph is given, use dep_graph given
    else:
        dep_graph = kws['dep_graph']
    # If not in runtime debugging mode, cache dependency graph
    if not runtime_debug:
        os.makedirs(os.path.dirname(dep_graph_filepath), exist_ok=True)
        saveToExcel(dep_graph_filepath, dep_graph)
    callgraph = dep_graph
    # endregion
    
    topk_list = range(1, 6)
    prkS = [0] * len(topk_list)
    acc = 0
    for i in range(testrun_round):
        if verbose and verbose >= 3:
            # verbose level >= 3: print random walk starting info
            print("{:^15}Randwalk round:{}".format("", i))
            print(
                "{:^15}Starting randwalk at({}): {}".format(
                    "", frontend, data_head[frontend - 1]
                )
            )
        rank, P = relaToRank(rela, callgraph, 10, frontend, rho=rho, print_trace=False)
        acc += my_acc(rank, true_root_cause, n=len(data))
        for j, k in enumerate(topk_list):
            prkS[j] += prCal(rank, k, true_root_cause)

        if verbose and verbose > 1:
            # verbose level >= 2: print random walk rank results
            print("{:^15}".format(""), end="")
            for j in range(len(rank)):
                print(rank[j], end=", ")
            print("")

    for j, k in enumerate(topk_list):
        prkS[j] = float(prkS[j]) / testrun_round
    acc /= testrun_round
    # Display PR@k and Acc if disable_print is not set
    if 'disable_print' not in kws or kws['disable_print'] is False:
        print_prk_acc(prkS, acc)
    if save_data_fig:
        saveToExcel(
            os.path.join(
                "monitor_rank",
                "results",
                data_source,
                "transition_prob_ela{}.xlsx".format(pc_aggregate),
            ),
            P.tolist(),
        )
        draw_weighted_graph(
            P.tolist(),
            os.path.join(
                "monitor_rank",
                "results",
                data_source,
                "transition_graph_ela{}.png".format(pc_aggregate),
            ),
        )
    return prkS, acc
```

