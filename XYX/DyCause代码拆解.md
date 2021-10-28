# main_dycause.py

## import

***line 1->32***

- argparse:？
- defaultdict:？
- datetime:？
- threading:线程
- os:操作系统？
- pickle:？
- random:随机数
- time:时间
- numpy:数组
- ThreadPoolExecutor：线程盆？
- matplotlib.pyplot:画图工具
- networkx:？
- statsmodels.api：？

- tqdm:？
- anomaly_detect:错误侦测 看文档anomaly_detect.md
- loop_granger:
- get_segment_split:
- get_ordered_intervals:
- get_overlay_count:
- normalize_by_row, normalize_by_column:
- randwalk:
- ranknode:
- analyze_root:
- load:
- draw_weighted_graph:
- prCal,:
- my_acc:
- pr_stat:
- print_prk_acc:
- format_to_excel:
- saveToExcel:



## 函数test_dycause line35:495

### 参数

- data_source="real_micro_service",
- aggre_delta=1,
- start_time=None,
- before_length=300,
- after_length=300,

**基于格兰杰区间的图构造参数**

- step=50,
- significant_thres=0.05,
- lag=5, # must satisfy: step > 3 * lag + 1
- auto_threshold_ratio = 0.8,

**路径因果图构造参数**

- testrun_round=1,
- frontend=14,
- max_path_length=None,
- mean_method="arithmetic",
- true_root_cause=[6, 28, 30, 31],
- topk_path=60,
- num_sel_node=1,

**debug 参数**

- plot_figures=False：//是否绘制结果图
- verbose=True：是否启用运行时调试模式
- runtime_debug=False,
- *args,
- **kws：？



## 过程

1. debug参数的初始化 line73:85
2. 'data' in kws 是什么意思，这里按照data在不在kws里面对data变量和data_head变量赋值 line87:98
3. 判断是否画图，需要的话调用画图函数draw_alldata
4. 运行时调试，赋值 time_stat_dict['Data load phase'] = toc-tic
5. 异常检测,定位开始时间，异常分数 line 117:126
6. 选择异常的区间 line 139:143
7. 为异常数据画图
8. 运行时调试，赋值 time_stat_dict['Anomaly detection phase'] = toc-tic
9. 区域运行loop_granger获取所有的间隔

   1. **是不是在写文件？内容是程序开始的一些信息** line 178:229
   2. 函数体内定义函数granger_process，使用了loop_granger函数（但好像没有调用到）
10. 区域定义线程池执行版本

    1. 定义函数thread_func,调用了granger_process函数
    2. 循环地将thread_func插入到执行者中
    3. 循环地提取granger执行的结果，并获得指定的区间（有异常的）
11. 使用得到的区间区域地构造影响图，通过叠加间隔，在两个服务之间生成动态因果曲线

    1. 计算覆盖次数overlay_counts = get_overlay_count(local_length, intervals)
    2. 画图
12. 使用比较和自动阈值从1个节点做边
    1. 添加边，为边赋值
13. 通过边的权重估计构建过渡矩阵
14. 往回广度搜索 line 411:452
    1. 使用了analyze_root函数，计算出按照是异常原因可能性排名的点和新的矩阵（这个矩阵后面都没用上）
15. 输出