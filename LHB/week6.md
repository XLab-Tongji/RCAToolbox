# MicroRCA: Root Cause Localization of Performance Issues in Microservices

#### Introduction

1.我们提出了一个带有服务和主机节点的属性图来模拟基于容器的微服务环境中的异常传播。

2.提供了一种通过将服务性能症状与相应的资源利用相关联来识别异常服务的方法，该方法很好地适应了微服务的异构性。

#### MicroRCA大致流程

1.数据收集模块从应用程序和系统级别（以前的论文大多只根据应用程序级别的指标识别根因，如果前端服务没有受到影响，则无法对系统故障进行定位）收集指标。应用程序级别的指标，特别是微服务的响应时间，用于检测性能问题，系统级度量包括容器和主机资源利用率。

2.一旦检测到异常，原因分析引擎构造一个带有服务和主机节点的属性图G来表示异常的传播路径。

3.接下来，引擎根据检测到的异常提取异常子图SG，并推断出哪个服务最可能引起异常。

#### 数据收集

从服务网格[26]和监视系统中分别收集应用程序和系统级别度量，并将它们存储在时间序列数据库中。在基于容器的微服务中，系统级度量包括容器和主机资源利用率，如图1中的“模型概述”中的容器和主机所示。应用程序级度量包括两个通信服务之间的响应时间等。

#### 异常检测

异常检测是根因定位的起点。MicroRCA利用无监督学习算法Distance-Based online clustering BIRCH 作为异常检测方法。我们使用微服务的慢响应时间作为异常的定义。

#### 原因分析引擎

当检测到异常时，原因分析引擎开始定位根本原因。该引擎由三个主要程序组成:属性图构造、异常子图提取和故障服务定位。引擎构造一个属性图来表示通过服务和主机的异常传播。然后，提取异常子图，并使用名为Personalized PageRank[28]的图中心性算法定位故障服务。

#### figure2：

##### 1.属性图

MicroRCA构造了一个属性图来表示微服务环境中的异常传播，其依据是观察到异常不仅沿着服务调用路径在服务之间传播，而且还传播到位于相同(虚拟)机器上。

属性图包含一组服务节点S = {s1, s2，…， sk}和主机节点H = {h1, h2，…， hm}，、对于每个服务节点si，我们为它与之通信的所有其他服务sj以及它运行的所有主机hk添加边。
通过解析在应用程序和系统级别上监视的度量来发现图节点及其动态关系。当服务si向服务sj发送请求时，我们添加一条从si到sj的有向边。如果在主机hj中分配了一个容器化的服务si，我们从si添加一条有向边到hj。
为了构造属性图，使用异常被检测到之前某个时间段的度量。我们假设所有的微服务在这段时间内可靠地运行，并且所收集的指标能够精确地提供所有通信服务和所定位主机之间的关系。图2(b)显示了来自初始微服务环境的一个构造的属性图的示例。

##### 2.异常子图

在构造属性图之后，我们继续根据检测到的异常提取异常子图，并将异常相关的属性分配给节点。异常子图SG是一个连接的子图，它表示通过服务和主机的异常传播。注意，我们使用通信服务之间的响应时间，它们是属性图中服务节点之间的边，作为异常检测目标。一旦确定一条边的响应时间为异常，我们将该边视为异常边，将该边的原点视为异常节点。

##### 3.计算异常边权值和异常节点得分

为了得到异常子图，我们首先提取异常服务节点。在图2(a)中，(s1, s2)、(s2, s3)、(s2, s4)之间的响应时间是不规则的。因此，我们提取出异常边，并取这些边的原点(在本例中为s2、s3、s4)作为异常服务节点。图2(c)将不规则边缘描述为虚线，将不规则服务节点描述为阴影节点。接下来，我们计算每个异常服务节点(记为rt a)对节点属性的平均异常响应时间。最后，我们添加连接到异常服务节点的节点和边。图2(c)为提取的异常子图，其中相邻服务节点s1、s5和相邻主机节点h1、h2可能受到影响

# Automated Anomaly Detection and Root Cause Analysis in Virtualized Cloud Infrastructures

（云平台但不是微服务的）

#### 异常检测：

对每个组件、应用程序加装异常检测器，一旦在给定时间确定了一组异常，有关异常的信息将被发送到异常关联引擎，该引擎试图通过根本原因分析来确定异常的来源。（图2）



#### 异常传播路径：

1.垂直传播：

物理机的异常导致虚拟机异常、虚拟机的异常导致物理机异常，同一物理机上的虚拟机之间导致异常（比如某一虚拟机消耗过大资源）

2.水平传播

比如web应用和后端数据库之间

获取异常传播路径

![截屏2021-11-18 下午5.58.33.png](https://pic.baixiongz.com/uploads/2021/11/18/7ae7cede0595e.png)

#### 根据异常传播路径集合构建异常传播图

Gc（Vc，Ec）

将每一个原点作为原点，构建一个Gc，其中Vc是当前源点能够根据异常传播路径到达的所有异常节点集，Ec则是以c为原点的所有异常传播边集合。

#### 根因定位

Gc覆盖异常节点数最多的，就最可能是根因。



# ADGS: Anomaly Detection and Localization based on Graph Similarity in Container-based Clouds

#### Introduction

本文提出了一种基于图相似度(ADGS)的基于docker云环境的异常检测与根本原因定位方法。我们首先监控应用程序中每个组件的响应时间和资源使用情况，以确定系统状态是否正常。然后，提出了一种基于图相似度的异常根源定位机制，研究了异常在聚类构件间的传播规律。我们在基于docker的环境中实现和计算方法。结果表明，该方法能有效、准确地检测和确定异常的根本原因。

#### 系统状态图：

通过通过组件之间的依赖关系以及组件与物理机之间的关系的部署信息构造。

组件：一种是代表运行在容器中的组件的顶点，另一种是代表物理机器的顶点。

边：图的边也有两种类型。一个是有向边，表示组件之间的依赖关系。边的权值表示启动组件的组件响应时间。另一种是无向边，它表示组件与物理机器的关联关系，无向边的权重表示组件的资源利用率。

![1637245196890.png](https://pic.baixiongz.com/uploads/2021/11/18/067da71ae1068.png)

异常导致系统状态图变化。

1.应用组件缺失

2.物理机缺失

3.边权值异常

异常检测：

计算正常与异常情况下图的相似度，返回异常顶点。

# GBDT(梯度增强决策树)

#### Introduction

(1)通过分析软件运行时资源层的KPI (Key Performance Indicator)，建立性能故障类型集，提取性能日志中强相关的性能特征。利用预警日志的分析结果，对性能日志进行合理的性能故障类型标注。
(2)利用同类型的平均填充以及SMOTE (Synthetic Minority过采样技术)和欠采样方法的结合，处理了该类型的不完全性能日志和非均衡化问题，保证了样本的有效性和均衡化。
(3)利用GBDT (Gradient Boosting Decision Tree)算法构造一个
性能故障诊断模型。
(4)通过部署在云平台上的一个防灾系统的实证案例研究，验证了所提方法对SaaS软件系统的性能诊断具有较高的效率和准确性。
本文的其余部分组织如下:第2节介绍了本文的研究背景和相关工作;第3节详细描述了我们的方法;第四节描述了实验设置;第五部分介绍实验过程及结果分析;第6部分对本文进行总结，并概述未来工作的方向。

预处理：

将性能日志与有监督的GBDT算法(梯度增强决策树)相结合，进行性能故障诊断。因此，用于构建模型的每个性能日志都有一个或多个明确的学习目标或注释，即性能故障类型。但是，实际获得的性能日志往往没有标注性能故障类型，因此需要标注日志类型。首先，我们需要对告警日志进行分析，确定每个告警日志的故障类型。然后使用警告日志的时间、状态、组件和故障类型对性能日志进行正确的标注。
一些监视工具记录生成的状态更改系统形成一些警告日志,通常包括时间或者时间戳的警告,警告的状态,和详细描述信息的警告,警告的级别,和特定的组件的警告,等等。

# Anomaly detecting and ranking of the cloud computing platform by multi-view learning(利用了ELM（极限学习机)）



#### Introduction

提出了一种基于机器学习理论的在线异常检测模型。然而，现有的基于机器学习的分类方法大多将不同子系统的所有特征直接链接到一个长特征向量中，难以既利用子系统之间的互补信息又忽略多视图特征来提高分类性能。针对上述问题，该方法对多视角特征进行自动融合，并对判别模型进行优化，以提高识别精度。该模型利用极限学习机(ELM)来提高检测效率。ELM是单隐层神经网络，它将输出权值的迭代解转化为线性方程组的解，并避免局部最优解。然后根据样本与分类边界之间的关系对异常进行排序，然后对排序后的异常赋权，最后对分类模型进行再训练。

1. 提出了一种基于ELM（一个前向传播的神经网络）的多视角学习在线异常检测方法，无需人工干预。

2. 该模型通过充分利用互补信息，获得当前特征下的最优解空间，通过迭代最小化训练误差，实现多视角特征根据监督信息自动融合多个子系统。

3. 通过提出新的模型进行后处理对异常进行排序，然后生成权重对分类模型进行再训练，以增强对不平衡分布的鲁棒性。

4. 通过学习，管理了高速数据流、高维索引集、异常分布不平衡等各种挑战。

   #### ELM：

   1.输入层和隐含层的连接权值、隐含层的阈值可以随机设定，且设定完后不用再调整

   2.隐含层和输出层之间的连接权值β不需要迭代调整，而是通过解方程组方式一次性确定。

   

##### 还有一篇是关于使用自组织地图（SOM）进行训练来识别根因的
