# RCAToolBox

## 介绍

根因分析算法工具箱。

## 构建顺序

1. 在base里找到目标基类；
2. 首先实现data_reader、data_loader（已完成）；
3. 实现ad_model（异常检测模型）；
4. 实现rca_model（根因分析模型）；
5. 实现localization（定位模型）；
6. 实现runner（具体的根因算法组合）；
7. 配置好config，运行算法。

## 测试运行

运行请参见test_runner.py。

## 缺少模块

- 日志记录模块；
- 评估模块。

