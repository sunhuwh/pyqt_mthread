import time

from log import show_message


class MailService:
    """邮件处理"""

    def send(self, my_window, mail_addresses, mail_index, test_error=False):
        """
        发送邮件
        :param mail_addresses:
        :param mail_index:
        :return:
        """
        mail_address = mail_addresses[mail_index]
        if mail_index == 1:
            i = 1
            while i <= 1000000000:
                print("my_window.mails_error", my_window.mails_error)
                if len(my_window.mails_error) > 0:
                    print(len(my_window.mails_error))
                    break
                print("i", i)  # 输出i
                i += 1
        if test_error:
            if mail_index == 3:
                raise Exception("处理错误")
            if mail_index == 6 or mail_index == 7 or mail_index == 8:
                show_message(my_window, "%s 运行中" % mail_address)
                j = 1
                while j <= 500:
                    if len(my_window.mails_error) > 1:
                        break
                    print("j", j)  # 输出j
                    j += 1
                    # time.sleep(1)  # 休眠1秒1234567
                show_message(my_window, "%s 运行完成" % mail_address)
        return mail_address