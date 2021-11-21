# Latent error prediction and fault localization for microservice applications by learning from system trace logs

## 简介
MEPEL(Microservice Error Prediction and Fault Localization)

基于定义在系统日志上的特征集,使用系统级和微服务级的日志来训练预测模型,从而预测潜在的错误、故障微服务以及实例的故障类型

## 预测模型
### 故障类型
- 整体故障
- 多实例故障
- 配置错误
- 异步交互故障:异步调用的执行或者返回顺序不符合预期

### 特征定义

