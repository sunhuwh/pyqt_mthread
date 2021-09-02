import time
# 显示log信息
def show_message(self, msg, level="info"):
    if self.is_debug:
        print(msg)
    time_curr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    # self.result_txt.append("<p></p>")/
    text = time_curr + "      " + msg
    if level == "error":
        text = "<p style='color: red'>"+"错误:"+text+"</p>"
    elif level == "success":
        text = "<p style='color: green'>"+"信息："+text+"</p>"
    elif level == "warn":
        text = "<p style='color: Gold'>"+"警告:"+text+"</p>"
    else:
        text = "<p style='color: black'>"+"信息："+text+"</p>"
    print("text", text)
    self.result_txt.append(text)
    # self.result_txt
    # self.result_txt.scroll(-1, -1)