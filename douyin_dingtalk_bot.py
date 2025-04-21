import time
import pickle
import os
import random
import pandas as pd
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from selenium.common.exceptions import (TimeoutException,
                                        NoSuchWindowException,
                                        WebDriverException)

# ========== 配置项 ==========
KEYWORD = "半天妖"
APP_KEY = "dingce5fhqvjiddwevmj"
APP_SECRET = "_ke87uRbkzzZ1-B53cgKP9FBsXr767YhX8XFkGJ442baxILKm6lyOp9SCQmuH3y6"
FORM_CODE = "QOG9lyrgJP3wrbe9tnGqd17GVzN67Mw4"
COOKIE_FILE = "douyin_cookies.pkl"
LOGIN_TIMEOUT = 300  # 延长至5分钟

class DouyinCrawler:
    def __init__(self):
        self.driver = None

    def init_driver(self):
        """初始化浏览器实例"""
        options = uc.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')

        # 设置真实用户代理
        user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        ]
        options.add_argument(f'user-agent={random.choice(user_agents)}')

        # 添加其他防检测参数
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        try:
            self.driver = uc.Chrome(
                options=options,
                headless=False,  # 必须可视化模式
                version_main=114  # 指定Chrome版本
            )
            # 注入stealth.js防检测
            with open('stealth.min.js') as f:
                js = f.read()
            self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": js
            })
            return True
        except Exception as e:
            print(f"[ERROR] 浏览器初始化失败: {str(e)}")
            return False

    def save_cookies(self):
        """保存Cookies到文件"""
        try:
            cookies = self.driver.get_cookies()
            with open(COOKIE_FILE, 'wb') as f:
                pickle.dump(cookies, f)
            print("[INFO] Cookies保存成功")
            return True
        except Exception as e:
            print(f"[ERROR] 保存Cookies失败: {str(e)}")
            return False

    def load_cookies(self):
        """从文件加载Cookies"""
        if not os.path.exists(COOKIE_FILE):
            return False

        try:
            with open(COOKIE_FILE, 'rb') as f:
                cookies = pickle.load(f)

            # 先访问域名以设置cookies
            self.driver.get("https://www.douyin.com")
            time.sleep(2)

            for cookie in cookies:
                # 修复domain格式
                if 'domain' in cookie:
                    if cookie['domain'].startswith('.'):
                        cookie['domain'] = cookie['domain'][1:]
                try:
                    self.driver.add_cookie(cookie)
                except Exception as e:
                    continue

            print("[INFO] Cookies加载完成")
            return True
        except Exception as e:
            print(f"[ERROR] 加载Cookies失败: {str(e)}")
            return False

    def check_login_status(self):
        """检查登录状态"""
        try:
            self.driver.get("https://www.douyin.com")
            time.sleep(random.uniform(2, 4))  # 随机延迟

            # 多种方式检测登录状态
            status_checks = [
                lambda: bool(self.driver.get_cookie("passport_csrf_token")),
                lambda: bool(self.driver.find_elements(By.XPATH, '//*[contains(@class, "avatar")]')),
                lambda: "login" not in self.driver.current_url
            ]

            return all(check() for check in status_checks)
        except:
            return False

    def douyin_login(self):
        """执行抖音登录流程"""
        print("[ACTION] 正在处理登录流程...")

        try:
            # 清除旧状态
            self.driver.delete_all_cookies()
            self.driver.get("about:blank")
            time.sleep(1)

            # 访问登录页
            login_url = "https://www.douyin.com/login"
            self.driver.get(login_url)
            time.sleep(random.uniform(3, 5))

            # 等待登录弹窗出现
            try:
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "login-form")]')))
                print("[INFO] 登录弹窗已出现")
            except TimeoutException:
                # 尝试手动触发登录
                try:
                    self.driver.find_element(By.XPATH, '//button[contains(text(),"登录")]').click()
                    time.sleep(3)
                except:
                    print("[WARNING] 无法找到登录按钮")
                    return False

            print("======================================")
            print("请完成以下步骤：")
            print("1. 使用抖音APP扫码")
            print("2. 完成短信验证（如有）")
            print(f"3. 请不要操作浏览器，等待程序自动检测（最多{LOGIN_TIMEOUT//60}分钟）")
            print("======================================")

            # 等待登录完成
            start_time = time.time()
            while time.time() - start_time < LOGIN_TIMEOUT:
                if self.check_login_status():
                    print("[INFO] 登录成功")
                    time.sleep(5)  # 确保完全加载
                    return self.save_cookies()

                # 随机延迟防止检测
                time.sleep(random.uniform(5, 10))
                print("[INFO] 等待登录完成...")

            print("[ERROR] 登录超时")
            return False

        except Exception as e:
            print(f"[ERROR] 登录过程中出错: {str(e)}")
            return False

    def search_videos(self, keyword):
        """执行搜索并获取数据"""
        print(f"[INFO] 正在搜索: {keyword}")
        results = []

        try:
            search_url = f"https://www.douyin.com/search/{keyword}?type=video"
            self.driver.get(search_url)
            time.sleep(random.uniform(5, 8))

            # 检查登录状态
            if not self.check_login_status():
                print("[WARNING] 登录状态失效")
                return pd.DataFrame()

            # 等待搜索结果加载
            try:
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, '//*[contains(@class, "search-content")]')))
            except TimeoutException:
                print("[WARNING] 搜索结果加载超时")
                return pd.DataFrame()

            # 缓慢滚动加载
            scroll_attempts = 0
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            while scroll_attempts < 5:
                # 随机滚动距离
                scroll_pos = random.randint(500, 1000)
                self.driver.execute_script(f"window.scrollBy(0, {scroll_pos});")
                time.sleep(random.uniform(2, 4))

                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    scroll_attempts += 1
                last_height = new_height

            # 提取视频数据
            video_items = self.driver.find_elements(By.XPATH, '//*[contains(@class, "video-card")]')
            print(f"[INFO] 找到 {len(video_items)} 个视频")

            for item in video_items[:20]:  # 限制数量
                try:
                    title = item.find_element(By.XPATH, './/*[contains(@class, "title")]').text
                    link = item.find_element(By.TAG_NAME, 'a').get_attribute('href')

                    if title and link:
                        results.append({
                            "title": title.strip(),
                            "link": link.split('?')[0]
                        })
                except Exception as e:
                    continue

            return pd.DataFrame(results)

        except Exception as e:
            print(f"[ERROR] 搜索过程中出错: {str(e)}")
            return pd.DataFrame()

    def run(self):
        """主运行流程"""
        print("====== 抖音数据采集器 ======")

        # 初始化浏览器
        if not self.init_driver():
            return

        try:
            # 登录流程（最多重试3次）
            max_retry = 3
            logged_in = False

            for attempt in range(max_retry):
                print(f"[INFO] 登录尝试 {attempt + 1}/{max_retry}")

                # 尝试加载已有cookies
                if self.load_cookies() and self.check_login_status():
                    print("[INFO] 使用已有cookies登录成功")
                    logged_in = True
                    break

                # 需要重新登录
                if self.douyin_login():
                    logged_in = True
                    break

                print(f"[WARNING] 登录失败，剩余尝试次数: {max_retry - attempt - 1}")
                time.sleep(5)

            if not logged_in:
                print("[ERROR] 多次登录失败，程序终止")
                return

            # 执行搜索
            df = self.search_videos(KEYWORD)

            if df.empty:
                print("\n[ERROR] 未获取到数据，可能原因:")
                print("1. 登录状态异常")
                print("2. 页面结构变化")
                print("3. 搜索结果为空")
                return

            print("\n抓取结果样例：")
            print(df.head())

            # 写入钉钉
            token = self.get_dingtalk_token()
            if not token:
                print("[ERROR] 钉钉认证失败")
                return

            self.write_to_dingtalk(token, df.to_dict("records"))

        except Exception as e:
            print(f"[CRITICAL] 主流程异常: {str(e)}")
        finally:
            self.close_driver()

    def get_dingtalk_token(self):
        """获取钉钉access_token"""
        print("[INFO] 获取钉钉AccessToken...")
        url = "https://oapi.dingtalk.com/gettoken"
        params = {"appkey": APP_KEY, "appsecret": APP_SECRET}
        try:
            res = requests.get(url, params=params, timeout=10)
            return res.json().get("access_token")
        except Exception as e:
            print(f"[ERROR] 获取token失败: {str(e)}")
            return None

    def write_to_dingtalk(self, token, data_list):
        """写入钉钉多维表格"""
        print("[INFO] 正在写入钉钉表格...")
        url = "https://api.dingtalk.com/v1.0/smartwork/forms/records"
        headers = {"x-acs-dingtalk-access-token": token}

        success_count = 0
        for item in data_list[:10]:  # 限制数量
            payload = {
                "formCode": FORM_CODE,
                "data": {
                    "标题": item.get("title", "")[:100],
                    "链接": item.get("link", "")
                }
            }
            try:
                res = requests.post(url, json=payload, headers=headers, timeout=10)
                if res.status_code == 200:
                    success_count += 1
                else:
                    print(f"[WARNING] 写入失败: {res.text}")
            except Exception as e:
                print(f"[ERROR] 写入异常: {str(e)}")

        print(f"[SUCCESS] 成功写入 {success_count}/{len(data_list)} 条数据")

    def close_driver(self):
        """关闭浏览器"""
        if self.driver:
            try:
                self.driver.quit()
                print("[INFO] 浏览器已关闭")
            except:
                pass

if __name__ == "__main__":
    crawler = DouyinCrawler()
    crawler.run()