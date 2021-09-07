import time

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal

# 继承 QObject
class TimeConsumingRunThread(QtCore.QObject):
    """
    定义耗时长的操作
    """

    # 通过类成员对象定义信号对象，可定义多个
    _signal = pyqtSignal(str)

    def __init__(self, main_handle):
        super(TimeConsumingRunThread, self).__init__()
        self._main_handle = main_handle
        self._main_handle.set_info_callback(self.success_back)

    def success_back(self, content):
        self._signal.emit(content)

    def __del__(self):
        print
        ">>> __del__"

    def run(self):
        start_time = int(time.time())

        # 调用任务线程操作
        self._main_handle.run()

        end_time = int(time.time())
        print("total_time", end_time - start_time)