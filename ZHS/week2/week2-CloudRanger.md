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
对于每个vi-vk-vj的V型结构
	如果vk不在S(vi,vj)和S(vj,vi)中,则定向为vi->vk<-vj
根据Rule1-3确定vi->vj方向
	若存在vi->vj,vi、vk不相邻,则定向vj-vk为vj->vk
	若存在vi->vk->vj,则定向为vi->vj
	若存在vi-vk->vj和vi-vl->vj,vk、vl不相邻,则定向vi-vj为vi->vj
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

#### 二阶随机游走
> I:In-neighbor O:Out-neighbor
##### 一阶随机游走
$v_i->v_j, p_{i,j}$,t时刻遍历到服务$X_t$此时条件概率$p_{i,j}=P[X_t=v_j|X_{t-1}=v_i]$
访问vj的概率与相关评分$c_{j,fe}$成正比,故转移概率矩阵P:
$$[P]_{i,j}=p_{i,j}=\frac{c_{j,fe}}{\Sigma_{l\in O_i}c_{l,fe}}$$
##### 向前转移
上一个访问的节点为vk,$$p_{k,i,j}=P[X_{t+1}=v_j|X_{t-1}=v_k,X_t=v_i]=P[X_{t+1}=v_j,X_t=v_i|X_{t-1}=v_k,X_t=v_i]$$
点到点的转移转化成边到边的转移$(v_k,v_i)->(v_i,v_j)$;
定义一个自回归模型$$p_{k,i,j}^{'} = (1-\beta)p_{k,i} + \beta p_{i,j}$$
边转移概率矩阵$M_{m\times m}$
$$[M]=p_{k,i,j}=\frac{p_{k,i,j}^{'}}{\Sigma_{l\in O_i}p_{k,i,j}^{'}}=\frac{(1-\beta)p_{k,i} + \beta p_{i,j}}{\Sigma_{l\in O_i}[(1-\beta)p_{k,i} + \beta p_{i,j,l}]}$$
##### 向后转移

$$p_{k,i,j}^b=\rho \frac{p_{k,i,j}^{'}}{\Sigma_{l\in I_i}p_{k,i,j}^{'}}=\rho \frac{(1-\beta)p_{k,i} + \beta p_{i,j}}{\Sigma_{l\in I_i}[(1-\beta)p_{k,i} + \beta p_{i,j,l}]}$$
##### 自转移
若无评分较高的邻接服务
$$p_{k,i,i}^s=max(0,p_{k,i,i}-\max\limits_{l\in I_i \cup O_i}p_{k,i,l})$$
```
Algorithm 2 Random Walk
Input: G,M,vfe
Output: R[n]
R[n], vs=vfe, vp=vfe
while(n)
	vp=vs
	计算前转概率
	计算后转概率
	计算自转概率,行标准化[M]ps
	从vs、Os、Is中随机选择一个vs
	R[s]++
给R[n]排序
```
