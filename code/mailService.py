from log import show_message


class MailService:
    """邮件处理"""

    def send(self, exec_queue, msg_text_browser, error_logs, mail_addresses, mail_index, info_callback, test_error=False):
        """
        发送邮件
        :param mail_addresses:
        :param mail_index:
        :return:
        """
        if not exec_queue.empty():
            return
        mail_address = mail_addresses[mail_index]
        try:
            if not test_error:
                i = 1
                while i <= 1000:
                    i += 1
                info_callback(mail_address)
            else:
                if mail_index == 3:
                    raise Exception("处理错误")
                if mail_index == 6 or mail_index == 7 or mail_index == 8:
                    show_message(msg_text_browser, "%s 运行中" % mail_address)
                    j = 1
                    while j <= 500:
                        j += 1
                    info_callback(mail_address)
                    show_message(msg_text_browser, "%s 运行完成" % mail_address)
        except Exception as e:
            error_logs[mail_addresses] = str(e)
            exec_queue.put("Termination")
            raise Exception(e)

        return mail_address