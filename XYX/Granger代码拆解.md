# Granger_all_code

[toc]

不理解的操作:

**array_target = array_data[:, index_target:index_target + 1].astype(float)**



## import line 7:23

## 函数test_granger line 26:84

### 参数

- array_data:数据集
- array_data_head:数据的header list
- feature: feature 的名称
- target: target 的名称
- lag: 滑动窗口大小
- significant_thres:

单个数据上的格兰杰测试

## class cnts_prune line 87:99

- cnt_promising
- cnt_promising_not
- cnt_not_sure
- cnt_initial

## 函数pick_a_date line 102:109

### 参数

- array_data:数据
- array_data_head:数据标头（应该是个索引？通过date查表得到索引再去array_data找）
- date:指定日期

提取出指定日期的数据

## 函数pick_a_trip line112:122

### 参数

- array_data:数据
- trip:坐标
- list_dividing_limit：索引表

取索引在list_dividing_limit[trip] : list_dividing_limit[trip+1]之间的数据

## 函数divide_the_trip line124:177

### 参数

- array_data:数据
- array_data_head:数据标头
- time_diff_thres：提取的时间差下限(秒)

### 过程

1. 读数据。line136:141
2. 逐行拆分data的时间并插入list_time列表中,最后转换为numpy列表array_time。line146:158
3. 提取时间差，得大于参数time_diff_thres，最后咋开头插入0，在list_dividing_limit末尾插入array_time大小。line 166:174
4. 返回list_dividing_limit, list_time_diff



## 函数interpolation line179：250

### 参数

- array_data:数据
- array_data_head:数据标头

### 重要变量

- interpolation_time_step：插入按照的时间间隔

### 过程

1. 同上
2. 同上
3. 看间隔，间隔小于interpolation_time_step，sample计数器加1，等于interpolation_time_step则都加1，大于interpolation_time_step，则**通过计算求得数据 line228:240 不太懂**



按照interpolation_time_step秒时间间隔对数据进行线性插值补全数据

## 函数loop_granger line 253:691

### 参数

- array_data: 时间序列数据，每列为一个变量
- array_data_head: 变量的名称
- path_to_output: 输出路径
- feature: Granger causality的源变量名称 (feature -> target)
- target: Granger causality的目标变量名称 (feature -> target)
- significant_thres: 假设检验的显著性水平
- test_mode: 不同优化实现方式，这里默认使用最好的优化方式，即fast_version_3
- trip: 选择时间序列的哪个时间段，只在simu_real为real时有效
- lag: Granger causality test的最大历史间隔（**滑动窗口大小**）
- step: 划分区间的最小步长
- simu_real: 是否为模拟或真实数据，在真实数据下将会作适当的数据插值
- max_segment_len:进行因果检验的最大区间长度
- min_segment_len:进行因果检验的最小区间长度
- verbose: whether print detailed info

### 重要变量

- addconst（True）:每次是否增加固定的值

- time_diff_thres:时间间隔下阈值
- min_trip_length:最小坐标间隔

### 步骤

1. 设置一些参数

2. 检测数据集的真实性

3. 按块裁剪数据

4. 选择区间

5. 通过插值使得数据样本间隔interpolation_time_step秒

6. 获得target和feature的index和array line350:354

7. 合并数组array_target和array_feature;反过来再合并一次得到array_XY和array_YX，这里应该是不确定XY是谁影响着谁。

8. list_segment_split = [step * i for i in range(n_step)]这里list_segment_spilt的值是[0,step,2\*step.....n_step\*step]

9. 设置进行loop的参数

   ```
   start = 0//没用上
   end = 0//没用上
   total_cnt_segment_YX = 0
   total_cnt_segment_XY = 0
   total_cnt_segment_adf = 0
   total_cnt_segment_cal_adf = 0
   total_cnt_segment_examine_adf_Y = 0
   ```

10. 设置操作数组

    ```
    array_results_YX = np.full((n_step + 1, n_step + 1), -2, dtype=float)
    array_results_XY = np.full((n_step + 1, n_step + 1), -2, dtype=float)
    
    array_adf_results_X = np.full((n_step + 1, n_step + 1), -2, dtype=float)
    array_adf_results_Y = np.full((n_step + 1, n_step + 1), -2, dtype=float)
    
    array_res2down_ssr_YX = np.full((n_step + 1, n_step + 1), -2, dtype=float)
    array_res2djoint_ssr_YX = np.full((n_step + 1, n_step + 1), -2, dtype=float)
    ```

11. 开始循环，外层循环 i 从0到n_step：

    - 分别设置XY和YX的参数

    - 内层循环j 从i+1到n_step+1：

      - 选择j所在位置为末尾

      - 如果分段长度过小或者过大都跳过因果检验

      - 选择不同的test_mode

        - call_package:

          1. 调用库函数granger_std计算Y对于X的关联p_value_YX

          2. 如果p_value_YX小于假设检验的显著性水平,再调用库函数计算X对于Y的关联p_value_XY

          3. 如果p_value_YX大于等于假设检验的显著性水平，置p_value_XY为-1.

             ```
             array_results_YX[i, j] = p_value_YX
             array_results_XY[i, j] = p_value_XY
             ```
          
         - standard:

           1. 调用函数grangercausalitytests(x, lag, addconst=True, verbose=False)；采用自定义的方法进行Granger causality检验，只对lag进行f test。
           2. 如果p_value_YX小于假设检验的显著性水平,再调用grangercausalitytests函数计算X对于Y的关联p_value_XY
           3. 同上3

         - fast_version_1:

           1. 调用函数grangercausalitytests_check_F_upper
           2. p_value_YX用grangercausalitytests_check_F_upper计算，p_value_XY用grangercausalitytests计算
           3. 同上3

        - fast_version_2:

          1. 调用函数grangercausalitytests_check_F_upper_lower
          2. p_value_YX用grangercausalitytests_check_F_upper_lower计算，p_value_XY用grangercausalitytests计算
          3. 同上3

        - fast_version_3:

          1. 调用函数grangercausalitytests_check_F_upper_lower
          2. 2个都用grangercausalitytests_check_F_upper_lower计算
          3. 同上3
          4. **有一个限制 Line559:575不懂**

12. **对结果进行判断？**

13. adfuller：可用于在存在序列相关的单变量过程中检验单位根

14. 再次筛选格兰杰的结果 line 593:624



## 函数get_lagged_data line691:727

### 参数

- x:data
- lag: 间隔
- addconst:增加的单位数
- verbose:

生成lag矩阵

对于列变量为[Y_t, X_t]的数据，调用下面语句之后会列变量变成
$[Y_t Y_{t-1} Y_{t-2} ... Y_{t-lag} X_{t-1} X_{t-2} ... X_{t-lag}] $

格兰杰算法中基本的分段函数

### 返回值

- dta: 整个lag矩阵
- dtaown: 只包含自己过去lag的矩阵, 即$[Y_{t-1} Y_{t-2} ... Y_{t-lag}]$
- dtajoint: 包含自己和其他变量过去lag时刻的数据，即$[Y_{t-1} Y_{t-2} ... Y_{t-lag} X_{t-1} X_{t-2} ... X_{t-lag}]$



## 函数fit_regression line 730:743

### 参数

- dta:数据
- dtaown：只包含自己过去lag的矩阵, 即$[Y_{t-1} Y_{t-2} ... Y_{t-lag}]$
- dtajoint: 包含自己和其他变量过去lag时刻的数据，即$[Y_{t-1} Y_{t-2} ... Y_{t-lag} X_{t-1} X_{t-2} ... X_{t-lag}]$

使用了OLS函数，最小二乘法函数

**这里计算2个value来判断Y和X的因果性**

针对部分模型和全模型进行两次线性拟合，并返回结果



## 函数f_test line746:773

### 参数

- res2down:只包含自己的矩阵计算出的最小二乘法的得到的结果
- res2djoint:包含其他变量的最小二乘法得到的结果
- lag:间隔

### 返回值

一个字典：

```
					{'ssr_ftest':
                       (F-statistics, 
                       stats.f.sf(fgc1, lag, res2djoint.df_resid)(p_value),
                       res2djoint.df_resid(完全模型剩余自由度)), 
                       lag)
                    }
```

根据拟合结果进行F统计检验，返回统计值

**格兰杰的F测试，判断res2down和res2djoint的大小是否有意义**



## 函数grangercausalitytests line776:790

采用自定义的方法进行Granger causality检验，只对lag进行f_test

而statsmodels里的方法会对从1到lag的间隔都采取4种假设检验，效率较低。

**这里应该是自己实现的f_test？？**



## 函数update_bound line793:833

### 参数

- x:用于补充未知拟合点的误差的数据
- pre_res2down:   前一步半模型结果
- pre_res2djoint: 前一步全模型结果
- pre_res2down_ssr_upper:之前独立变量的上界
- pre_res2down_ssr_lower:下界
- pre_res2djoint_ssr_upper:之前混合变量的上界
- pre_res2djoint_ssr_lower:下界
- pre_res2djoint_df_resid: 全模型的自由度
- lag:
- step: 每步使用样本量，用于确定补充误差需要使用的样本数量
- addconst, verbose: 用于产生lag数据

根据上一步的ssr计算当前这一步的ssr的上下界

## 函数grangercausalitytests_check_F_upper_lower line 836:947

### 参数

- x：data
- lag：间隔
- pre_res2down：之前的只包含自己的矩阵计算出的最小二乘法的得到的结果
- pre_res2djoint：之前的包含其他变量的最小二乘法得到的结果
- pre_res2down_ssr_upper,
- pre_res2down_ssr_lower,
- pre_res2djoint_ssr_upper,
- pre_res2djoint_ssr_lower,
- pre_res2djoint_df_resid,
- significant_thres,
- step,
- cnt,
- cnt_prune,
- addconst=True,
- verbose=False

### 步骤

1. 如果cnt=-1，说明还没有数据，**好像是重新跑一遍之前弄的东西**，获得数据
2. 如果cnt!=-1,将已经有的数据赋值，然后得到上下界，判断是否越界，越界则不要，没有则保留

自定义的F测试，考虑上界也考虑下界

## 函数grangercausalitytests_check_F_upper line 950:1007

### 参数

- x：data
- lag：间隔
- pre_res2down：之前的只包含自己的矩阵计算出的最小二乘法的得到的结果
- pre_res2djoint：之前的包含其他变量的最小二乘法得到的结果
- pre_res2down_ssr_upper,
- pre_res2djoint_ssr_lower,
- pre_res2djoint_df_resid,
- significant_thres,
- step,
- cnt,
- cnt_prune,
- addconst=True,
- verbose=False

### 步骤

1. 如果cnt=-1，说明还没有数据，**好像是重新跑一遍之前弄的东西**，获得数据
2. 如果cnt!=-1,将已经有的数据赋值，然后得到上下界，判断是否越界，越界则不要，没有则保留

自定义的F测试，只考虑独立变量的上界和混合变量的下界

