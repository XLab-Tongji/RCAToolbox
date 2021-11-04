论文推荐：

1.Fault Root Rank Algorithm Based on Random Walk Mechanism  in Fault Knowledge Graph

#### 1.调用关系图

服务依赖图：不同微服务之间。

wij为边ij的权重，wijk可理解为wij的第k维指标（两个顶点之间有多个维度指标），wijk对所有k求和结果为1.

#### 2.有条件的独立测试

假设X,Y,Z的子集定义在概率空间𝑆(Ω，𝑋，𝑃)中，如果P(X|Y,Z) = P(X|Z)，则X和Y在Z下是条件独立的，可以用X⊥Y|Z表示。为了判断连续数据的条件独立性，条件独立性的实质是判断X和Y在给定Z下的独立性，具体分为两个步骤:

1.分别计算X与Z的回归残差𝑟𝑋和Y与Z的回归残差𝑟𝑌。采用回归法计算残差;它们可以表示为𝑟𝑋=𝑋−𝛼⋅𝑍and𝑟𝑌=𝑌−𝛼⋅𝑍,𝛼变量的相关系数𝑋𝑌。

2.计算偏相关系数。计算残差rX、rY的相关系数及偏相关系数𝜌𝑋𝑌⋅𝑍。偏相关系数𝜌𝑋𝑌⋅𝑍= 0,当且仅当𝑋⊥𝑌|𝑍,但如果𝜌𝑋𝑌⋅𝑍!= 0表示𝑋⊥𝑌|𝑍未成立。

为了自动构建依赖图，论文从一个完全无向图开始，通过检查任意两个节点的独立性，逐步去除不相关节点之间的边，并最终确定边的方向。

```python
基于独立性测试的服务依赖图生成算法
Input: Metrics M, Vertex V, significance a, separation set S, Output: Reverse any edge direction in G

new G(V, E, W), level = 0
for ∀(vi,vj) ∈ V if |adj(G, vi,k)\{vj}| ≥ level
for ∀ Vm ⊂ adj(G,vi) with |m| = level for ∀ Mk ∈ M, k ∈ [1,m]
if vi,vj conditionally independent given Vm, a, Mk set Wi,j,k= 0
insert Vm into S(vi,vj,k) and S(vj,vi,k)
end if end for
end for
level ← level + 1
end for
for any i, j,k let Wi,j,k equals formula(2)
for ∀ vi − vj − vl ∈ G
if ∃k ∈ [1,m] make { vj not in S(vi,vl,k) and vj not in S(vl,vi,k) } true.
orient vi − vj− vl into vi→ vj← vl end if
end for
for adjacent V(X, Y, Z) in G
if Z ∉ C, and C is a set that splits paths between X and Y then replacethedirectionX-Y-ZwithX→Z←Y
end if
if X → Y - Z then
replace the direction Y - Z with Y → Z end if
if X - Z and X → Y → Z then
replace the direction X - Z with X → Z
end if
if X - Z and ∃ L, X - Y → Z and X - L → Z then
replace the direction X - Z with X → Z end if
end for Return G.
```

#### 3.改进的随机行走算法

简单的随机游走存在以下问题：

1.转移概率的计算问题不能很好地解释，随机只能用来模拟自然行走的过程。

2.没有针对特定情景进行专门的概率计算和分析，使得结果更加平均。因此，纯随机行走算法不适合路径生成场景

论文为了解决微服务场景下随机概率的可解释性问题，提出了<u>节点相似度计算公式</u>，并将其用于算法后续部分的转移概率计算。同时，设计了具体节点的正向、自传输(或称自旋)和向后传输公式。一般来说，在基于节点搜索可能的传播路径时，访问次数越多的节点更有可能是故障的根本原因。

#### 与monitorRank的最大不同：在构建依赖图时考虑了多维指标的影响（wijk表示微服务i和j在第k维指标上的影响权重比率）



2.Self-Adaptive Root Cause Diagnosis for Large-Scale Microservice Architecture

**MSrank的一稿多投。**

MSrank四个阶段：

(P1)构建影响图;(P2)随机行走诊断;(P3)结果精度评价;(P4)指标权重更新。检测到的系统事件触发MS-Rank以最近收集的度量为基础构建影响图。更具体地说，我们通过因果分析，从基于服务之间相关性的各种指标中提取影响图。然后根据影响图给出了随机游走诊断算法。这个过程产生每个服务的概率排名作为异常的根本原因。通过验证该结果的准确性，MS-Rank对每个服务的每个类型度量的置信权矩阵进行更新。这是一个在线递增的自适应过程，也是一个启发式框架。我们可以将其扩展到更复杂的解，并将其与专家知识相结合，以提高结果的精度和计算效率。

3.MFRL-CA:Microservice Fault Root Cause Location based on Correlation Analysis

论文工作：

(1)研究了微服务的依赖调用关系和服务执行路径。根据微服务相关的调用数据和故障数据，设计了端到端跟踪链路调用图(Link call Graph of end- end Tracking, LCGT)和微服务故障相关有向图(microservice Fault Correlation Directed Graph, FCDG)，并在上述两种故障传播图的基础上构造了描述微服务故障传播关系的MFPG。
(2)在故障根定位方面，优化了异常相关的计算方法，分析了传统随机游走算法的局限性，设计了一种三搜索方向的随机游走算法。最后，在上述研究的基础上，提出了MFRL-CA方法。提高了故障搜索范围的全局性、灵活性和准确性。
(3)根据上述方法，设计了MFRL-CA框架原型，并进行了实验验证。实验结果表明，该方法能快速、准确地定位故障的根本原因。

研究对象：微服务故障根因寻找

#### 1.故障检测

微服务故障发生后，需要在微服务故障发生前检测各机器kpi的变化情况。为了检测机器KPI的变化时间点，采用基于滑动窗口的CUSUM[17]变化点检测算法检测故障前机器KPI时间序列数据，准确识别机器KPI变化的开始时间。
通过以上过程，我们可以准确的标记出微服务故障发生后各机器KPI时间序列数据的变化时间点，并采集该时间点前后的时间序列数据。

#### 2.微服务故障传播关系图（本篇论文的特点）

微服务故障传播图模块:当微服务发生故障时，根据微服务请求的执行轨迹构造LCGT，根据故障关联关系构造FCDG。最后，将两个故障传播图构造为一个MFPG，用于描述故障传播扩散关系，缩小故障定位范围，并作为故障根因定位模块的输入。

(1)利用监控工具收集微服务节点之间的依赖调用和各种KPI数据。当微服务异常时，根据微服务的异常请求调用数据构建LCGT。(2)基于微服务的历史故障数据，提取微服务的故障事件，构建FCDG。(3)结合LCGT和FCDG，设计了MFPG构建方法。

LCGT：微服务间的依赖调用关系

FCDG：微服务间的影响关系
$$
MFPG=LCGT\cup FCDG
$$
（其中顶点与顶点合并，边与边合并）

### monitorRank代码：

```python
    #加载数据
    if 'data' not in kws:
        data, data_head = load(
            os.path.join("data", data_source, "rawdata.xlsx"),
            normalize=True,
            zero_fill_method='prevlatter',
            aggre_delta=pc_aggregate,
            verbose=verbose,
        )
        # Transpose data to shape [N, T]
        data = data.T#样例中的数据共16行，代表16个微服务，其中第16个是view（前端），每个微服务有300个数据记录。
        rela = calc_pearson(data, method="numpy", zero_diag=False)#计算皮尔森相关系数(获得16x16的矩阵)
```

```python
#获取调用图（测试代码直接从文件中读取了调用图，并以邻接矩阵的形式存储）
    if 'dep_graph' not in kws:
        if data_source == "pymicro":
            # 真实的调用拓扑矩阵
            dep_graph = readExl(os.path.join("data", data_source, "true_callgraph.xlsx"))
            print("dep_graph",dep_graph)
            print(len(dep_graph))
        elif data_source == "real_micro_service":
            # 如果它不在runtime_debug模式下，如果可能，保存并加载先前构造的图
            if os.path.exists(dep_graph_filepath) and not runtime_debug:
                # 如果先前的依赖关系图存在，则加载它。
                if verbose and verbose >= 2:
                    # verbose level >= 2: print dependency graph loading info
                    print(
                        "{:^10}Loading existing link matrix file: {}".format(
                            "", dep_graph_filepath
                        )
                    )
                dep_graph = readExl(dep_graph_filepath)
            else:
               #如果之前的依赖图不存在，使用PC算法生成它。
                if verbose and verbose >= 2:
                    # verbose level >= 2: print dependency graph construction info
                    print("{:^10}Generating new link matrix".format(""))
                dep_graph = build_graph_pc(data, alpha=pc_alpha)
    # 当PC调用图被给定时，则使用它。
    else:
        dep_graph = kws['dep_graph']

```

```python
def relaToRank(rela, access, rankPaces, frontend, rho=0.3, print_trace=False):
    n = len(access)
    S = [abs(_) for _ in rela[frontend - 1]]#提取前端与其他接口的皮尔森相关系数
    P = np.zeros([n, n])
    for i in range(n):
        for j in range(n):
            # 添加前向边权重
            if access[i][j] != 0:
                P[i, j] = abs(S[j])
            # 添加回边权重（rho为自己设定的值，这里设定为0.3）
            elif access[j][i] != 0:
                P[i, j] = rho * abs(S[i])
    # 添加自边权重
    for i in range(n):
        if i != frontend - 1:
            P[i][i] = max(0, S[i] - max(P[i]))
    P = normalize(P)

    teleportation_prob = (np.array(S) / np.sum(S)).tolist()#计算传送概率
    label = [i for i in range(1, n + 1)]
    l = firstorder_randomwalk(
        P, rankPaces, frontend, teleportation_prob, label,
        print_trace=print_trace
    )#进行随机游走，返回一个按根因评分排序的根因序列。
    # print(l)
    return l, P
  
```

```python

acc += my_acc(rank, true_root_cause, n=len(data))#计算平均准确率，在排名中正确的根因越靠前acc就越高。
```

```python
#计算prks（prks[j]表示：在得分排序表的前j个元组中，正确预测的根因个数占总根因数的比例）
for j, k in enumerate(topk_list):
            prkS[j] += prCal(rank, k, true_root_cause)
```

```python
def firstorder_randomwalk(
    P,#添加了自边、回边和权值的调用图
    epochs,
    start_node,#（前端节点，下标16）
    teleportation_prob,#传送概率
    label=[],#节点下标（1-16）
    walk_step=1000,#走1000步
    print_trace=False,
):
    n = P.shape[0]
    score = np.zeros([n])
    current = start_node - 1
    for epoch in range(epochs):
        if print_trace:
            print("\n{:2d}".format(current + 1), end="->")
        for step in range(walk_step):
            if np.sum(P[current]) == 0:
                current = np.random.choice(range(n), p=teleportation_prob)#如果概率全是0，则跳出该点，重新选取
                break
            else:
                next_node = np.random.choice(range(n), p=P[current])#否则按概率随机选取下一跳
                if print_trace:
                    print("{:2d}".format(current + 1), end="->")
                score[next_node] += 1#选中的节点分数加1
                current = next_node
    score_list = list(zip(label, score))
    score_list.sort(key=lambda x: x[1], reverse=True)
    return score_list
```

