# TBAC

## get_callers/get_callees

```python
"""
Find the callers/callees of node, using fixed search depth
Parameters
----------
access:PC依赖图
node:当前节点
search_depth:往上/下搜索的深度

Returns
-------
返回当前节点调用的节点和绝对（fixed）深度
"""
```

## weighted_powermean

```python
"""
Weighted power mean in TBAC

Params:
    score: scores list
    p: power exponent
    weight: weight for each score, same length as s
Returns:
    powermean result
"""
```

## correlation_algorithm

```python
"""

Parameters
----------
scores:异常分数表
access:PC图

Returns
-------
处理后的异常分数表
"""
```

1. 对于每个节点，求出callers和callees。

2. 求带权平均值S_in_mean（Caller至少存在1个）

3. 对上下的异常评分作比较，看看有没有需要调整的分数。

   ```python
   rating[node] = 0.5 * (scores[node] + 1)
   rating[node] = 0.5 * (scores[node] - 1)
   ```

## test_tbac

```python
"""
Parameters
----------
data_source:源数据
pc_aggregate:PC迭代的次数
pc_alpha：PC参数alpha
frontend：初始节点
true_root_cause:人为设置的真正的根因
verbose：输出过程参数
runtime_debug：帮助debug的输出过程打印参数
args：没用到
kws：参数表

Returns
-------
"""
```

1. 获取随机数

2. load 数据，获得数据矩阵和微服务名称

3. 运行皮尔森函数获得相关系数矩阵 rela

4. ```
   access_filepath = os.path.join(
           "tbac",
           "results",
           data_source,
           "access_agg{}_alpha{}_winstart{}_len{}.xlsx".format(pc_aggregate, pc_alpha, window_start,data.shape[1])
   )
   ```

   这里又获得一次文件路径干嘛？

5. 获取PC关系依赖图 access

   1. 已经有，就读取

   2. 没有就自己跑PC算法

6. 输出日志
7. 获得异常分数（-1,1） line 258
8. 对指数操作修改异常分数 line 261
9. 排序，选出异常等级高的服务

​      