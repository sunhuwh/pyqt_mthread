import queue
import time
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED, FIRST_EXCEPTION
from PyQt5 import QtWidgets, QtCore
import os
from PyQt5.QtCore import pyqtSignal, QThread

from log import show_message
from mailService import MailService
from ui.main_windows import Ui_MainWindow

_global_dict = {}
mail_service = MailService()

# 继承 QObject
class TimeConsumingRunThread(QtCore.QObject):
    """
    定义耗时长的操作
    """

    # 通过类成员对象定义信号对象，可定义多个
    _signal = pyqtSignal(str)
    # 定义异常错误
    _error_logs = {}

    def __init__(self):
        super(TimeConsumingRunThread, self).__init__()
        self.flag = True

    def __del__(self):
        print
        ">>> __del__"

    def run(self):
        self._error_logs = {}
        exec_queue = queue.Queue()
        my_windows = _global_dict["parent"]
        start_time = int(time.time())
        exist_error = False
        with ThreadPoolExecutor(max_workers=None) as executor:
            task_dict, task_list = {}, []
            for i in range(len(myWindow.mails)):
                mail = myWindow.mails[i]
                task = executor.submit(mail_service.send, exec_queue, self, mail, i, my_windows.test_error)
                task_dict[task] = mail
                task_list.append(task)
            wait(task_list, return_when=FIRST_EXCEPTION)
            # 反向序列化之前塞入的任务队列，并逐个取消
            for task in reversed(task_list):
                task.cancel()

            # 等待正在执行任务执行完成
            wait(task_list, return_when=ALL_COMPLETED)
            exist_error = False
            for task in task_list:
                if task_dict.get(task):
                    target = task_dict.get(task)
                    if "finished returned NoneType" in str(task) or task.cancelled():
                        exist_error = True
                        self._signal.emit(",".join([target, "true"]))
                        print("{}被取消".format(target))
                    elif "finished raised Exception" in str(task):
                        exist_error = True
                        print("{}执行异常".format(target))
                        self._signal.emit(",".join([target, "true"]))
                        my_windows.mails_error.append(target)
                        show_message(my_windows, "文件转换异常：%s" % target, "error")
                        show_message(my_windows, self._error_logs[target], "error")
                        # 如果异常就将线程池关掉，以免还进行后续操作
                        print("线程关闭")
                        executor.shutdown()
                    else:
                        print("{}执行成功".format(target))
        if not exist_error:
            print("整体运作正常")
        end_time = int(time.time())
        print("total_time", end_time - start_time)

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
        self.time_consuming_thread = TimeConsumingRunThread()  # 1. 初始化自定义线程对象,耗时长的在这里
        self.thread_root = QThread(self)  # 2.创建QT线程
        _global_dict["parent"] = self

        self.time_consuming_thread.moveToThread(self.thread_root)  # 3.自定义线程移到QT线程中
        self._startThread_my_signal.connect(self.time_consuming_thread.run)  # 4.创建信号-槽 通过信号-槽启动线程处理函数，只能通过 _startThread.emit()来出发
        self.time_consuming_thread._signal.connect(self.call_backlog)  # 5.创建信号回调函数，通过self.signal.emit(mail)


    def submit(self):
        self.progressBar.setStyleSheet(
            "QProgressBar {   border-radius: 5px;   text-align: center;}")
        if self.thread_root.isRunning():  # 如果该线程正在运行，则不再重新启动
            return
        # mywindows = global_dict["parent"]
        self.mails_error = []
        self.mails_done = []
        show_message(self, "邮件发送中")
        self.pushButton.setText("发送中")
        self.pushButton.setEnabled(False)
        self.progressBar.setValue(0)

        """先启动子线程,再启动主线程"""
        self.time_consuming_thread.flag = True
        self.thread_root.start()
        # 发送信号，启动线程处理函数
        # 不能直接调用，否则会导致线程处理函数和主线程是在同一个线程，同样操作不了主界面
        self._startThread_my_signal.emit()

    def stop(self):
        show_message(self, "主线程停止")
        self.pushButton.setText("开始发送")
        self.pushButton.setEnabled(True)
        if not self.thread_root.isRunning():  # 如果该线程已经结束，则不再重新关闭
            return
        self.time_consuming_thread.flag = False
        self.stop_thread()

    def call_backlog(self, all_msg):
        msgs = all_msg.split(",")
        if len(msgs) > 1:
            self.stop()
            self.progressBar.setStyleSheet(
                "QProgressBar {  border-radius: 5px;   background-color: red;}QProgressBar::chunk {   background-color: #007FFF;   width: 10px;}QProgressBar {   border-radius: 5px;   text-align: center;}")
            # self.progressBar.setColor("red")
        else:
            msg = msgs[0]
            if msg:
                self.mails_done.append(msg)
                self.progressBar.setValue(int((len(self.mails_done) / len(self.mails) * 100)))
                show_message(self, "%s已发送" % msg, "success")
                if len(self.mails_done) == len(self.mails):
                    show_message(self, "已全部发送", "success")
                    self.stop()

    def stop_thread(self):
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

    def clear_result(self):
        self.result_txt.setText("")

    def open_out_dir(self):
        os.startfile(self.out_folder)

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
    # exit_error = True
    exit_error = False
    main(exit_error)