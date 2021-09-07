import queue
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED, FIRST_EXCEPTION

from log import show_message
from main import mail_service

class TaskThread():
    """
    多线程任务
    """
    signal = None
    info_callback = None

    def __init__(self, result_txt, test_error, target_error, targets):
        super(TaskThread, self).__init__()
        self.result_txt = result_txt
        self.test_error = test_error
        self.target_error = target_error
        self.targets = targets
        self._error_logs = {}

    def set_info_callback(self, emit):
        self.info_callback = emit

    def run(self):
        """
        必须定义run方法，出发就用run方法触发
        """
        exec_queue = queue.Queue()
        self._error_logs = {}
        exist_error = False
        with ThreadPoolExecutor(max_workers=None) as executor:
            task_dict, task_list = {}, []
            for i in range(len(self.targets)):
                target = self.targets[i]
                task = executor.submit(mail_service.send, exec_queue, self.result_txt, self._error_logs,
                                       target, i, self.info_callback, self.test_error)
                task_dict[task] = target
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
                        self.finished_noneType_cancel_callback(target)
                    elif "finished raised Exception" in str(task):
                        exist_error = True
                        self.finished_exception_callback(target, executor)
                    else:
                        self.finished_success(target)
        if not exist_error:
            self.all_success_callback()

    def finished_exception_callback(self, target, executor):
        """
        任务异常
        """
        print("{}执行异常".format(target))
        self.info_callback(",".join([target, "true"]))
        self.target_error.append(target)
        show_message(self.result_txt, "email发送异常：%s" % target, "error")
        show_message(self.result_txt, self._error_logs[target], "error")
        # 如果异常就将线程池关掉，以免还进行后续操作
        print("线程关闭")
        executor.shutdown()

    def finished_none_type_cancel_callback(self, target):
        """
        任务取消或者为None
        """
        self.info_callback(",".join([target, "true"]))
        print("{}被取消".format(target))

    def finished_success(self, target):
        """
        任务成功
        """
        print("{}执行成功".format(target))

    def all_success_callback(self):
        """
        整个线程任务全部执行成功
        """
        print("整体运作正常")