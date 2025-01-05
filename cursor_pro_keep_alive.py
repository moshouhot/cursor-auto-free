"""
Cursor Pro 自动化注册工具

@file cursor_pro_keep_alive.py
@description 
    自动化处理 Cursor 账号注册流程，包括：
    - 浏览器自动化控制
    - 验证码处理
    - 邮箱验证
    - token 获取与更新
    - ID 重置
@requires
    - DrissionPage
    - logging
    - random
    - time
@author yuyan peng
"""

import os
import time
import random
import logging
from cursor_auth_manager import CursorAuthManager
from browser_utils import BrowserManager
from get_email_code import EmailVerificationHandler
from logo import print_logo
from cursor_reset import reset_cursor_ids

# 设置环境变量
os.environ["PYTHONVERBOSE"] = "0"
os.environ["PYINSTALLER_VERBOSE"] = "0"

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("cursor_keep_alive.log", encoding="utf-8"),
    ],
)


def handle_turnstile(tab):
    """
    处理 Turnstile 验证码挑战
    
    @param {DrissionPage.Tab} tab - 浏览器标签页对象
    @returns {boolean} - 验证成功返回 True，失败返回 False
    @throws {Exception} - 验证过程中的异常
    @description
        - 查找并点击 Turnstile 验证码元素
        - 通过检查后续页面元素判断验证是否成功
        - 包含随机延时以模拟人工操作
    @example
        tab = browser.latest_tab
        success = handle_turnstile(tab)
    """
    print("\n开始突破验证码挑战...")
    try:
        while True:
            try:
                challengeCheck = (
                    tab.ele("@id=cf-turnstile", timeout=2)
                    .child()
                    .shadow_root.ele("tag:iframe")
                    .ele("tag:body")
                    .sr("tag:input")
                )

                if challengeCheck:
                    print("开始突破")
                    time.sleep(random.uniform(1, 3))
                    challengeCheck.click()
                    time.sleep(2)
                    print("突破成功")
                    return True
            except:
                pass

            if tab.ele("@name=password"):
                print("突破成功")
                break
            if tab.ele("@data-index=0"):
                print("突破成功")
                break
            if tab.ele("Account Settings"):
                print("突破成功")
                break

            time.sleep(random.uniform(1, 2))
    except Exception as e:
        print(e)
        print("突破失败")
        return False
    

def get_cursor_session_token(tab, max_attempts=3, retry_interval=2):
    """
    获取 Cursor 会话 token，带有重试机制
    
    @param {DrissionPage.Tab} tab - 浏览器标签页对象
    @param {number} max_attempts - 最大尝试次数，默认 3 次
    @param {number} retry_interval - 重试间隔(秒)，默认 2 秒
    @returns {string|None} - 成功返回 session token，失败返回 None
    @throws {Exception} - Cookie 获取失败时的异常
    @description
        - 从浏览器 cookie 中提取 WorkosCursorSessionToken
        - 支持多次重试
        - 包含错误处理机制
    """
    print("开始获取Cursor cookie")
    attempts = 0

    while attempts < max_attempts:
        try:
            cookies = tab.cookies()
            for cookie in cookies:
                if cookie.get("name") == "WorkosCursorSessionToken":
                    return cookie["value"].split("%3A%3A")[1]

            attempts += 1
            if attempts < max_attempts:
                print(
                    f"第 {attempts} 次尝试未获取到CursorSessionToken，{retry_interval}秒后重试..."
                )
                time.sleep(retry_interval)
            else:
                print(f"已达到最大尝试次数({max_attempts})，获取CursorSessionToken失败")

        except Exception as e:
            print(f"获取cookie失败: {str(e)}")
            attempts += 1
            if attempts < max_attempts:
                print(f"将在 {retry_interval} 秒后重试...")
                time.sleep(retry_interval)

    return None


def update_cursor_auth(email=None, access_token=None, refresh_token=None):
    """
    更新 Cursor 的认证信息
    
    @param {string|None} email - 新的邮箱地址
    @param {string|None} access_token - 新的访问令牌
    @param {string|None} refresh_token - 新的刷新令牌
    @returns {boolean} - 更新成功返回 True，失败返回 False
    @description
        - 使用 CursorAuthManager 更新本地认证信息
        - 支持选择性更新各项认证信息
    @requires CursorAuthManager
    """
    auth_manager = CursorAuthManager()
    print("开始更新Cursor本地认证信息")
    return auth_manager.update_auth(email, access_token, refresh_token)


def sign_up_account(browser, tab):
    """
    注册 Cursor 账号的完整流程
    
    @param {DrissionPage} browser - 浏览器实例
    @param {DrissionPage.Tab} tab - 浏览器标签页对象
    @returns {boolean} - 注册成功返回 True，失败返回 False
    @throws {Exception} - 注册过程中的任何异常
    @description
        - 访问注册页面并填写表单
        - 处理 Turnstile 验证码
        - 处理邮箱验证
        - 获取账号使用限额信息
        - 记录账号信息到日志
    @requires
        - handle_turnstile()
        - EmailVerificationHandler
    """
    print("开始注册Cursor账号...")
    tab.get(sign_up_url)

    try:
        if tab.ele("@name=first_name"):
            tab.actions.click("@name=first_name").input(first_name)
            time.sleep(random.uniform(1, 3))

            tab.actions.click("@name=last_name").input(last_name)
            time.sleep(random.uniform(1, 3))

            tab.actions.click("@name=email").input(account)
            time.sleep(random.uniform(1, 3))

            tab.actions.click("@type=submit")

    except Exception as e:
        print("打开注册页面失败")
        return False

    handle_turnstile(tab)

    try:
        if tab.ele("@name=password"):
            tab.ele("@name=password").input(password)
            time.sleep(random.uniform(1, 3))

            tab.ele("@type=submit").click()
            print("提交Cursor注册")

    except Exception as e:
        print("执行失败")
        return False

    time.sleep(random.uniform(1, 3))
    if tab.ele("This email is not available."):
        print("执行失败")
        return False

    handle_turnstile(tab)

    while True:
        try:
            if tab.ele("Account Settings"):
                break
            if tab.ele("@data-index=0"):
                print("接收邮箱验证码")
                code = email_handler.get_verification_code(account)
                if not code:
                    return False

                i = 0
                for digit in code:
                    tab.ele(f"@data-index={i}").input(digit)
                    time.sleep(random.uniform(0.1, 0.3))
                    i += 1
                break
        except Exception as e:
            print(e)

    handle_turnstile(tab)
    wait_time = random.randint(3, 6)
    for i in range(wait_time):
        print(f"等待中... {wait_time-i}秒")
        time.sleep(1)
    tab.get(settings_url)
    try:
        usage_selector = (
            "css:div.col-span-2 > div > div > div > div > "
            "div:nth-child(1) > div.flex.items-center.justify-between.gap-2 > "
            "span.font-mono.text-sm\\/\\[0\\.875rem\\]"
        )
        usage_ele = tab.ele(usage_selector)
        if usage_ele:
            usage_info = usage_ele.text
            total_usage = usage_info.split("/")[-1].strip()
            print("可用上限: " + total_usage)
    except Exception as e:
        print("获取可用上限失败")
    print("注册完成")
    account_info = f"\nCursor 账号： {account}  密码： {password}"
    logging.info(account_info)
    time.sleep(5)
    return True


class EmailGenerator:
    """
    随机邮箱生成器
    
    @class
    @description
        - 生成随机邮箱地址
        - 管理默认账号信息（密码、姓名等）
        - 支持自定义邮箱域名
    
    @property {string} domain - 邮箱域名
    @property {string} default_password - 默认密码
    @property {string} default_first_name - 默认名字
    @property {string} default_last_name - 默认姓氏
    """

    def __init__(
        self,
        domain="mailto.plus",
        password="".join(
            random.choices(
                "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*",
                k=12,
            )
        ),
        first_name="yuyan",
        last_name="peng",
    ):
        self.domain = domain
        self.default_password = password
        self.default_first_name = first_name
        self.default_last_name = last_name

    def generate_email(self, length=8):
        """
        生成随机邮箱地址
        
        @param {number} length - 随机字符串长度，默认 8
        @returns {string} - 生成的邮箱地址
        @description
            - 生成随机字符串
            - 添加时间戳
            - 拼接域名
        """
        random_str = "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=length))
        timestamp = str(int(time.time()))[-6:]  # 使用时间戳后6位
        return f"{random_str}{timestamp}@{self.domain}"

    def get_account_info(self):
        """
        获取完整的账号信息
        
        @returns {dict} - 包含邮箱、密码、姓名的账号信息字典
        @description
            - 生成新的随机邮箱
            - 返回所有默认账号信息
        """
        return {
            "email": self.generate_email(),
            "password": self.default_password,
            "first_name": self.default_first_name,
            "last_name": self.default_last_name,
        }


if __name__ == "__main__":
    """
    主程序入口
    
    @description
        执行完整的 Cursor 账号注册流程：
        1. 初始化浏览器和邮箱处理器
        2. 生成随机账号信息
        3. 执行注册流程
        4. 获取并更新认证信息
        5. 重置 Cursor ID
    
    @handles
        - 浏览器资源管理
        - 异常处理和日志记录
        - 程序退出清理
        - 执行时间统计
    """
    print_logo()
    browser_manager = None
    start_time = time.time()  # 记录开始时间
    
    try:
        # 初始化浏览器
        browser_manager = BrowserManager()
        browser = browser_manager.init_browser()

        # 初始化邮箱验证处理器
        email_handler = EmailVerificationHandler(browser)

        # 固定的 URL 配置
        login_url = "https://authenticator.cursor.sh"
        sign_up_url = "https://authenticator.cursor.sh/sign-up"
        settings_url = "https://www.cursor.com/settings"
        mail_url = "https://tempmail.plus"

        # 生成随机邮箱
        email_generator = EmailGenerator()
        account = email_generator.generate_email()
        password = email_generator.default_password
        first_name = email_generator.default_first_name
        last_name = email_generator.default_last_name

        auto_update_cursor_auth = True

        tab = browser.latest_tab
        # 尝试重置 Turnstile 验证码组件
        # turnstile.reset() 用于刷新验证码状态，如果组件不存在则忽略错误
        tab.run_js("try { turnstile.reset() } catch(e) { }")

        tab.get(login_url)
       
        if sign_up_account(browser, tab):
            token = get_cursor_session_token(tab)
            if token:
                update_cursor_auth(
                    email=account, access_token=token, refresh_token=token
                )
                # 在成功注册后自动重置ID
                print("\n开始重置Cursor ID...")
                if reset_cursor_ids():
                    print("Cursor ID重置成功！")
                else:
                    print("Cursor ID重置失败！")
            else:
                print("账户注册失败")

        print("执行完毕")
        # 计算并打印总执行时间
        end_time = time.time()
        duration = end_time - start_time
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        print(f"\n总共耗时: {minutes}分{seconds}秒")

    except Exception as e:
        logging.error(f"程序执行出错: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
    finally:
        if browser_manager:
            browser_manager.quit()
        input("\n按回车键退出...")
