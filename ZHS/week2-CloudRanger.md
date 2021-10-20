# CloudRanger: Root Cause Identification for Cloud Native Systems
> Auther: potassiummmm
## Intro
> What on earth is Cloud Native???
### Cloud Native的优势
- 横向设计(?),持续交付
- 容器交付(打包)
- 动态管理
- 面向微服务
- 高内聚,低耦合
 
### 微服务的问题及挑战
- 太多,难以监控、管理
- 更新迭代快,动态性使得更加难以对容器进行追踪
- 性能评估时需要对每一个微服务构造baseline,任务量大
- 出现问题若未能及时解决,会导致连锁反应,蔓延到整个服务网络
> 一种解决办法:断路器模式(中介监控失败次数,超过阈值则"断路"),但是不利于快速解决问题
> 
> 扩展:云设计模式

### Cloud Ranger介绍
一种新型的Cloud native系统性能管理方法,分为四步:
- 异常检测
- 构造影响图
- 相关性分析
- 根因确认

### Cloud Ranger特点
- 无需对业务进行跟踪和聚合(故不受动态性和baseline影响)

## Related Works
> baseline
## Background and Motivation
> dataset
## Solution: Cloud Ranger
### 问题定义
假设服务集合V中的一个前端服务$v_{fe}$在时间段[1,t]内出现异常

取$n×t$二维矩阵$T$,  $T_{i,j}=t_{i,j}$表示V中的某一服务$v_i$在j时刻的metric data

目标:给定T,找到V的一个子集$v_{rc}$,其导致了观测到的异常
### 框架
- 异常检测:除去正常的服务,找出候选项
- 构造影响图
- 相关性计算
- 根因调查

### 异常检测
> 利用了作者之前的[方案](https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=8034965)
>
> TODO 没看论文方案
- Time window: 异常检测的时间区间,文章重点即时间窗口的选择,从实验中得出结论:优先考虑时间间隔为5s时的情况

### 构造影响图
基于服务之间的内部相关性通过因果关系构造,假设为有向无环图DAG

#### 影响图
> TODO 还没看完

G(V,E),可能包括有向边和无向边
- 存在边:有条件依赖
- 有向边:vi影响vj
- 无向边:至少有一个DAG中包含vi->vj and vj->vi

设V为输入顶点集,给定显著性水平α∈ (0,1),影响图构造包括四个步骤:
- 在V上生成一个完全无向图
- 基于α测试给定邻接集上的条件独立性,如果被接受,则删除边
- Orient v-structures
- 确定剩余边的方向
> v-structure: A->C<-B
>
> d-separation:确定贝叶斯网络中变量独立性的方法,将三变量关系递归推广
>
> d-separated:给定DAG模型,当且仅当vi和vj在任一服务集S的子集上都条件独立,称vi和vj被S d-separated,记为函数S(vi,vj)

```
Algorithm 1 Impact Graph Construction
Input: V, S, α
Output: G

在V上生成一个完全无向图, level = 0
遍历所有vi-vj边:
	如果与i相邻的顶点数(不包括j)大于等于level
		遍历相邻顶点集合大小为level的子集Vk
			如果vi、vj在Vk条件下条件独立
				删除vi-vj边
				把Vk加入S(vi,vj)和S(vj,vi)
	level++

// 确定方向
```

### 相关性计算
#### idea
如果两个服务在给定的metric序列下有相似的异常模式,那么应该是被相同的根因所影响导致的
#### 评估函数
Pearson相关性函数$C_{i,j}$
### 根因确认
#### 假设
只有影响图G和相关度C
#### 随机遍历
- 启发式的:不仅要考虑当前服务的相关性,还要考虑遍历过的服务之间的关系
> 例如,在随机漫步期间,当上一个节点和当前节点的相关性都很高时,向前移动而不是向后进行故障排除,更可能找到根本原因.

#### 二阶随机漫步
> TODO 有点杂,没看完
