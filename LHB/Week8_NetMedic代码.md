# Week8_NetMedic代码

### 代码总结

除了采用PC算法构建调用图外，其他部分基本上与论文所述方法相同。

#### 计算异常度

```python
def compute_abnormality(data, history_range, current_range):
    n = len(data)
    mu = np.mean(data[:, slice(*history_range)], axis=1, keepdims=True)
    sigma = np.std(data[:, slice(*history_range)], axis=1, keepdims=True)
    v = np.mean(data[:, slice(*current_range)], axis=1, keepdims=True)
    devia = (v - mu) / (np.sqrt(2)*sigma)
    abnormal = 1-2*gaussian.sf(np.abs(devia))
    return abnormal
```

#### 计算边权值

```python
def compute_edgeweight(data,
                       impact_graph,
                       history_range,
                       current_range,
                       bin_size=100,
                       delta=0.33):
    n = data.shape[0]

    hist_data = data[:, slice(*history_range)]
    curr_data = data[:, slice(*current_range)]

    K = max(min(50, int(hist_data.shape[1]/bin_size)), 1)
    hist_state = divide_mean(hist_data, K)
    curr_state = np.mean(curr_data, axis=1)
    var_max = np.max(data, axis=1)
    var_min = np.min(data, axis=1)

    def calc_diff(v_k, v_now, i):
        return abs(v_k - v_now)/(var_max[i] - var_min[i])

    edge_weight = np.zeros([n, n])
    for source in range(n):
        for destination in range(n):
            if impact_graph[source, destination] > 0:
                weight = 0.0
                w_k_sum = 0.0
                for k in range(K):
                    source_diff = calc_diff(
                        hist_data[source, k], curr_state[source],
                        source)
                    w_k = 1 - source_diff if source_diff <= delta else 0
                    w_k_sum += w_k
                    weight = weight + \
                        (1-calc_diff(
                            hist_state[destination, k],
                            curr_state[destination],
                            destination))*w_k
                if w_k_sum <= 0.0:
                    edge_weight[source, destination] = 0.8
                else:
                    edge_weight[source, destination] = weight/w_k_sum

    return edge_weight
```

#### 计算最大路径权值

```python
def compute_impact_matrix(impact_graph, edge_weight):
    n = edge_weight.shape[0]
    impact = np.zeros([n, n])
    for c in range(n):
        for e in range(n):
            if e == c:
                impact[c, e] = 1.0
            else:
                all_path = enum_path(impact_graph, c, e)
                impact[c, e] = compute_max_path_weight(all_path, edge_weight)
    return impact
```

#### 计算全局影响分数

```python
def compute_global_impact(impact_matrix, abnormality):
    n = impact_matrix.shape[0]
    global_impact = np.zeros(n)
    for c in range(n):
        s = 0.0
        for e in range(n):
            s += impact_matrix[c, e]*abnormality[e]
        global_impact[c] = s
    return global_impact
```

#### 根因分数计算

```python
    for i in range(data.shape[0]):
        node_score.append(
            (i + 1, 1 / (impact_matrix[i, affected_node - 1] * global_impact[i]))#将两个分数合并起来
        )
    node_score.sort(key=lambda x: x[1])
```

