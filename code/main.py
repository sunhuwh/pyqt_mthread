#!/usr/bin/python
# coding:UTF-8
"""
description: 解决pyQT在多线程环境下，任务时间长导致页面假死问题以及多线程下任务异常问题
解决方案：
1. 定义一个子进程，专门做长时间操作
2. 子进程中如果有多线程，并且多线程下，如果某个任务异常，则终止所有剩余任务（当然，也可以自定义不终止所有）
"""
from PyQt5 import QtWidgets
import os
from PyQt5.QtCore import pyqtSignal, QThread

from TaskThreadService import *
from TimeConsumingRunThreadService import TimeConsumingRunThread
from log import show_message
from mailService import MailService
from ui.main_windows import Ui_MainWindow

_global_dict = {}
mail_service = MailService()

class myWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    mails = ["111.qq.com", "222.qq.com", "333.qq.com", "444.qq.com", "555.qq.com", "666.qq.com", "777.qq.com"]
    files_checked = []
    process = 0
    mails_done = []
    mails_error = []
    is_debug = True
    out_folder = None
    done_mails_numbers = 0
    test_error = False

    _startThread_my_signal = pyqtSignal()

    def __init__(self):
        super(myWindow, self).__init__()
        self.setupUi(self)
        self.progressBar.setStyleSheet(
            "QProgressBar {   border-radius: 5px;   text-align: center;}QProgressBar::chunk {   background-color: #007FFF;   width: 10px;}")
        self.pushButton.clicked.connect(self.submit)

        """
        多线程
        """
        task_thread = TaskThread(self.result_txt, self.test_error, self.mails_error, self.mails)
        self._time_consuming_thread = TimeConsumingRunThread(task_thread)
        # 1. 初始化自定义线程对象,耗时长的在这里
        self.thread_root = QThread(self)
        # 2.创建QT线程
        _global_dict["parent"] = self
        # 3.自定义线程移到QT线程中
        self._time_consuming_thread.moveToThread(self.thread_root)
        # 4.创建信号-槽 通过信号-槽启动线程处理函数，只能通过 _startThread.emit()来出发
        self._startThread_my_signal.connect(self._time_consuming_thread.run)
        self._time_consuming_thread._signal.connect(self.call_backlog)  # 5.创建信号回调函数，通过self.signal.emit(mail)

    def submit(self):
        self.progressBar.setStyleSheet(
            "QProgressBar {   border-radius: 5px;   text-align: center;}")
        if self.thread_root.isRunning():  # 如果该线程正在运行，则不再重新启动
            return
        self.mails_error = []
        self.mails_done = []
        show_message(self.result_txt, "邮件发送中")
        self.pushButton.setText("发送中")
        self.pushButton.setEnabled(False)
        self.progressBar.setValue(0)

        """先启动子线程,再启动主线程"""
        self.thread_root.start()
        # 发送信号，启动线程处理函数
        # 不能直接调用，否则会导致线程处理函数和主线程是在同一个线程，同样操作不了主界面
        self._startThread_my_signal.emit()

    def stop(self, callback):
        """通用"""
        if callback is not None:
            callback()
        if not self.thread_root.isRunning():  # 如果该线程已经结束，则不再重新关闭
            return
        self.stop_thread()

    def process_error_style(self):
        """通用"""
        self.progressBar.setStyleSheet(
            "QProgressBar {  border-radius: 5px;   background-color: red;}QProgressBar::chunk {   background-color: #007FFF;   width: 10px;}QProgressBar {   border-radius: 5px;   text-align: center;}")

    def stop_call_back(self):
        """自定义结束线程后"""
        self.pushButton.setText("开始发送")
        self.pushButton.setEnabled(True)

    def call_backlog(self, all_msg):
        """自定义子线程传过来的数据处理"""
        msgs = all_msg.split(",")
        if len(msgs) > 1:  # 当消息长度超过1，那么就代表有处理异常
            self.stop(self.stop_call_back)
            self.process_error_style()
        else:
            msg = msgs[0]
            if msg:
                self.mails_done.append(msg)
                self.progressBar.setValue(int((len(self.mails_done) / len(self.mails) * 100)))
                show_message(self.result_txt, "%s已发送" % msg, "success")
                if len(self.mails_done) == len(self.mails):
                    show_message(self.result_txt, "已全部发送", "success")
                    self.stop(self.stop_call_back)

    def stop_thread(self):
        """通用"""
        print
        ">>> stop_thread... "
        # if not self.time_consuming_thread.flag:
        #     self.time_consuming_thread
        if not self.thread_root.isRunning():
            return
        self.thread_root.quit()  # 退出
        self.thread_root.wait()  # 回收资源
        print
        ">>> stop_thread end... "

def main(test_error=False):
    import sys
    app = QtWidgets.QApplication(sys.argv[:1])
    ui = myWindow()
    ui.setWindowTitle("多线程假死测试工具")

    ui.test_error = test_error
    ui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    # 测试有error和没有error的情况
    exit_error = True
    # exit_error = False
    main(exit_error)