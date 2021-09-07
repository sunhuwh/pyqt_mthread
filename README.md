# pyqt_mthread

## pyqt多线程假死解决方案

1. 主要使用主线程和子线程分离，子线程处理耗时长的任务，主线程处理主逻辑
2. 子线程中包含多线程任务的，解决子线程中某任务异常，停止其余任务

## 文件定义
1. log 日志
2. mailService 邮件服务
3. main.py 主函数
4. TaskThreadService 任务服务，子线程中的多线程任务
5. TimeConsumingRunThreadService 子线程（处理耗时长的）