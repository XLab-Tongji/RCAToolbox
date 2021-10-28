# anomaly_detect

[toc]



## 函数 anomaly_detect：



### 参数：(括号内为默认值) line11:19

- data:数据，多列，每一列代表一个变量
- weight(1):权重分配
- mean_interval(60):测量标准偏差的滑动窗口，第一个时间戳内的异常评分为0
- anomaly_proportion(0.3):一个异常变量被看做是异常的几率，与weight关联。**是不是异常变量也不一定是异常的？**
- verbose(True):**在debug的时候打印等级？**0 (Nothing), 1 (Method info), 2 (Phase info), 3(Algorithm info)
- save_fig(True):
- path_output(None):

### 返回值

- start_index:数据中的异常源点

### 变量：line 34:35

- data_ma:**貌似是滑动窗口的累加平均？**
- data_std:全局标准差

### 函数moving_average：line37:40

#### 参数:（括号内为默认值）line 37

- a:要处理的data
- n(3):宽度

#### 过程： line 38：40

- np.cumsum() 逐行累加函数
- ret将传入的data累加
- ret按操作修改值
- 操作：ret[n:] = ret[n:] - ret[:-n]     #ret[n:],除了前n个，ret[:-n],除了后n个
- 操作：return ret[n - 1 :] / n #对位除n，因为line 38累加了

### 过程 line 42：126

#### line 42:51

- **不知道为什么要间隔col，col还是递增的**

#### line 53:58

- np.std()计算标准差,**同样不知道为什么要间隔递增的col

#### line 62:65

- 如果权重都是一样的，对每一行，大于1的数做count得到每一行**出现了异常**？的个数

#### line57:71

- argsort()函数是将x中的元素从小到大排列，提取其对应的index(索引)，然后输出

#### line 72:87

- 展示上述结果

#### line 88:123

- 保存数据，并画图
