"""
邮箱验证码获取模块。

本模块提供自动从临时邮箱服务获取验证码的功能。
"""

from DrissionPage.common import Keys
import time
import re


class EmailVerificationHandler:
    """
    邮箱验证码处理器类。

    该类提供与临时邮箱服务(特别是tempmail.plus)交互的方法，
    用于获取通过邮件发送的验证码。

    属性:
        browser: 用于网页交互的浏览器实例
        mail_url (str): 临时邮箱服务的URL地址
    """

    def __init__(self, browser, mail_url="https://tempmail.plus"):
        """
        初始化邮箱验证码处理器。

        参数:
            browser: 用于网页自动化的浏览器实例
            mail_url (str, 可选): 临时邮箱服务的URL地址，默认为 "https://tempmail.plus"
        """
        self.browser = browser
        self.mail_url = mail_url

    def get_verification_code(self, email):
        """
        从临时邮箱获取验证码。

        参数:
            email (str): 需要检查验证码的邮箱地址

        返回:
            str|None: 如果找到验证码则返回验证码，否则返回 None
        """
        username = email.split("@")[0]
        code = None

        try:
            print("正在处理...")
            # 打开新标签页访问临时邮箱
            tab_mail = self.browser.new_tab(self.mail_url)
            self.browser.activate_tab(tab_mail)

            # 输入用户名
            self._input_username(tab_mail, username)

            # 等待并获取最新邮件
            code = self._get_latest_mail_code(tab_mail)

            # 清理邮件
            self._cleanup_mail(tab_mail)

            # 关闭标签页
            tab_mail.close()

        except Exception as e:
            print(f"获取验证码失败: {str(e)}")

        return code

    def _input_username(self, tab, username):
        """
        在临时邮箱服务中输入用户名。

        参数:
            tab: 浏览器标签页实例
            username (str): 要输入的用户名
        """
        while True:
            if tab.ele("@id=pre_button"):
                tab.actions.click("@id=pre_button")
                time.sleep(0.5)
                tab.run_js('document.getElementById("pre_button").value = ""')
                time.sleep(0.5)
                tab.actions.input(username).key_down(Keys.ENTER).key_up(Keys.ENTER)
                break
            time.sleep(1)

    def _get_latest_mail_code(self, tab):
        """
        获取最新邮件中的验证码。

        参数:
            tab: 浏览器标签页实例

        返回:
            str|None: 如果找到验证码则返回验证码，否则返回 None
        """
        code = None
        while True:
            new_mail = tab.ele("@class=mail")
            if new_mail:
                if new_mail.text:
                    tab.actions.click("@class=mail")
                    break
                else:
                    break
            time.sleep(1)

        if tab.ele("@class=overflow-auto mb-20"):
            email_content = tab.ele("@class=overflow-auto mb-20").text
            verification_code = re.search(
                r"verification code is (\d{6})", email_content
            )
            if verification_code:
                code = verification_code.group(1)
                print("马上就要成功了")
            else:
                print("执行失败")

        return code

    def _cleanup_mail(self, tab):
        """
        清理邮件。

        参数:
            tab: 浏览器标签页实例
        """
        if tab.ele("@id=delete_mail"):
            tab.actions.click("@id=delete_mail")
            time.sleep(1)

        if tab.ele("@id=confirm_mail"):
            tab.actions.click("@id=confirm_mail")
