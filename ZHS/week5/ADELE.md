# ADELE: Anomaly Detection from Event Log Empiricism

## 架构图
![image](https://github.com/XLab-Tongji/RCAToolbox/blob/File/ZHS/week5/prediction_framework_overview.png)

## 摘要
一种用于数据存储系统中的早期异常检测的经验数据驱动方法

从系统日志中仔细选择特征,并开发用于异常检测的机器学习技术

从系统自身的历史中学习,建立正常行为的基线,并识别系统出现问题的时间段

## 异常检测
子系统生成事件日志可能可以用于检测整个系统的异常

### 周期性和异常线索
子系统生成的事件日志似乎展现出周期性

如果一个或者多个子系统处于异常阶段,那么日志的某些属性中会体现出来(如出现不规则)

### 工程日志属性
- 事件计数
- 事件发生比例
- 平均到达间隔(子系统连续事件之间的平均间隔)
- 平均到达距离(模块连续事件之间其他子系统的平均事件数)
- 传播严重程度
- 时间间隔分布

### 特征表示:日志转换
第d天的特征矩阵
$$X_d={X_{i,j}^{(d)} where i \in M and j \in A}$$
M是模块集合(子系统),A是属性集合

## ADELE
针对每个bug训练模型,收集日志,将每天的日志转化为得分矩阵,作为特征表示.利用被视为问题特征的系数向量作为模型,进行训练.

### 个体特征的异常得分
使用正态分布进行拟合
正态分布下的累计分布函数(CDF)
$$CDF(X_{i,j}) = \frac{1}{\sigma _{i,j}\sqrt{2\pi}}e^{-(X_{i,j}-\mu_{i,j})^2/2\sigma _{i,j}^2}$$

其中
$X_{i,j}$为特征值,$\mu_{i,j}$、$\sigma_{i,j}$分别为平均差和标准差
计算得$X_{i,j}$的异常得分为
$$S_{i,j} = 2*|0.5-CDF(X_{i,j})|$$
将其作为异常值的度量,分析该值和正常值的偏差


![image](https://github.com/XLab-Tongji/RCAToolbox/blob/File/ZHS/week5/anomaly_identification_process.png)



### 系统状态标签
观测得出:异常信号通常出现在两周前,故标记两周前以及一周后的日期进行标记

### 估算系统异常得分
对于不同子系统,特征的贡献值不同
使用岭回归进行学习,得到权重向量w
