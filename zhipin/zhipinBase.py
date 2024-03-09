import datetime
import json
import os
import re
import shutil
import sys
import time
from urllib.parse import parse_qs, urlparse
from PIL import Image
import cv2
import httpx
from httpx import HTTPError
from parameterized import parameterized
import pytest
from captcha import cracker
from filelock import FileLock
from zhipin import ZhiPin
from seleniumbase import BaseCase
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    NoSuchElementException,
    ElementNotVisibleException,
)
from jd import JD
from chat import Chat

BaseCase.main(__name__, __file__)


class ZhiPinBase(BaseCase, ZhiPin):
    def init(self):
        ZhiPin.__init__(self)
        self.set_default_timeout(self.config_setting.timeout)
        self.http_headers = {
            "User-Agent": self.execute_script("return navigator.userAgent;"),
        }
        self.WAIT = WebDriverWait(self.driver, self.config_setting.timeout)
        if (
            self.config_setting.cookies_name
            and not os.getenv("CI")
            and not os.getenv("PYTEST_XDIST_WORKER")
        ):
            self.cookies_driver = self.get_new_driver(
                browser="chrome",
                headless=False,
                undetectable=True,
                switch_to=False,
                chromium_arg=None,
            )
            self.set_cookies()
            self.chat = Chat()
            self.COOKIES_WAIT = WebDriverWait(
                self.cookies_driver, self.config_setting.timeout
            )

    def set_cookies(self):
        original_driver = self.driver
        self.driver = self.cookies_driver
        self.open(self.URL1)
        self.sleep(self.config_setting.sleep_long)
        self.load_cookies(self.config_setting.cookies_name)
        self.sleep(self.config_setting.sleep_long)
        self.open(self.URL1)
        self.driver = original_driver

    @parameterized.expand(
        [["SeleniumBase Commander", "Commander"]]
        * int(os.environ.get("PYTEST_XDIST_WORKER_COUNT", 1))
    )
    def test_jobs(self, arg1, arg2):
        self.init()
        if "PYTEST_XDIST_WORKER" in os.environ:
            self.captcha_lock = FileLock("captcha.lock")
            self.iterate_job_parameters_xdist()
        else:
            self.iterate_job_parameters()

    def iterate_job_parameters_xdist(self):
        worker_str = os.environ.get("PYTEST_XDIST_WORKER")
        match = re.search(r"\d+$", worker_str)
        if match:
            self.worker_id = int(match.group())
        else:
            self.worker_id = None
        self.worker_count = int(os.environ.get("PYTEST_XDIST_WORKER_COUNT"))
        self.executed_params = []
        if os.path.exists("executed_params.json"):
            with open("executed_params.json", "r", encoding="utf-8") as f:
                try:
                    self.executed_params = json.load(f)
                except json.JSONDecodeError:
                    self.executed_params = []
        for city in self.config_setting.query_city_list:
            for query in self.config_setting.query_list:
                for salary in self.config_setting.salary_list:
                    for page in range(
                        self.config_setting.page_min, self.config_setting.page_max
                    ):
                        params = (city, query, salary, page)
                        if (
                            params in self.executed_params
                            or page % self.worker_count != self.worker_id
                        ):
                            continue
                        self.execute_find_jobs(*params)
                        self.executed_params.append(params)
                        with open("executed_params.json", "w", encoding="utf-8") as f:
                            json.dump(self.executed_params, f, ensure_ascii=False)
        self.cursor.close()
        self.conn.close()

    def execute_find_jobs(self, city, query, salary, page):
        try:
            self.find_jobs(
                self.URL1
                + query
                + self.URL7
                + city
                + self.URL2
                + salary
                + self.URL3
                + str(page)
            )
        except (
            TimeoutException,
            StaleElementReferenceException,
            NoSuchElementException,
        ) as e:
            self.handle_exception(e)

    def find_jobs(self, page_url):
        query_list = self.query_jobs(page_url)
        pass_card_list = self.check_card(query_list)
        self.process_detail(pass_card_list)

    def query_jobs(self, page_url):
        self.open(page_url)
        url_list = []
        try:
            element_list = self.WAIT.until(
                ec.any_of(
                    ec.presence_of_all_elements_located(
                        (By.CLASS_NAME, "job-card-wrapper")
                    ),
                    ec.presence_of_element_located(
                        (By.CLASS_NAME, "job-empty-wrapper")
                    ),
                )
            )
        except (TimeoutException, StaleElementReferenceException) as e:
            self.handle_exception(e, f",page_url:{page_url}")
            self.check_dialog()
            self.check_verify()
            return url_list
        if not isinstance(element_list, list):
            return url_list
        for element in element_list:
            element: WebElement
            try:
                jd = JD()
                job_info = element.find_element(
                    value="[class*='job-info clearfix']", by=By.CSS_SELECTOR
                )
                job_info_html = job_info.get_attribute(
                    "innerHTML",
                )
                jd.communicated = not self.is_ready_to_communicate(job_info_html)
                url = element.find_element(
                    value=" .job-card-left", by=By.CSS_SELECTOR
                ).get_attribute("href")
                id = self.get_encryptJobId(url)
                row = self.get_jd(id)
                if row and row.id == id:
                    if self.config_setting.skip_known:
                        self.sleep(self.config_setting.sleep)
                        continue
                    else:
                        jd = row
                jd.url = url.split("&securityId")[0]
                jd.name = element.find_element(
                    value=" .job-name", by=By.CSS_SELECTOR
                ).text
                jd.city = element.find_element(
                    value=" .job-area", by=By.CSS_SELECTOR
                ).text
                jd.company = element.find_element(
                    value=" .company-name a", by=By.CSS_SELECTOR
                ).text
                jd.industry = element.find_element(
                    value=" .company-tag-list    li", by=By.CSS_SELECTOR
                ).text
                jd.checked_date = datetime.datetime.now()
                jd.id = id
                print(jd)
                self.update_jd(jd)
                if self.check_jd(jd, "query"):
                    url_list.append(url)
            except Exception as e:
                self.handle_exception(e, f",page_url:{page_url},element:{element.text}")
                continue
        self.conn_commit()
        return url_list

    def check_card(self, url_list):
        pass_list = []
        for url in url_list:
            query_params = parse_qs(urlparse(url).query)
            lid = query_params.get("lid", [None])[0]
            security_id = query_params.get("securityId", [None])[0]
            try:
                self.open(
                    self.URL4 + security_id + self.URL5 + lid + self.URL6,
                )
                self.wait_for_element_present(selector="pre", by=By.TAG_NAME)
                page_source = self.find_element(selector="pre", by=By.TAG_NAME).text
                data = json.loads(page_source)
                if data["message"] != "Success":
                    raise Exception(data)
                else:
                    print(data)
                    jd = self.get_jd(self.get_encryptJobId(url))
                    jd.url = url.split("&securityId")[0]
                    jd.description = data["zpData"]["jobCard"]["postDescription"]
                    jd.active = data["zpData"]["jobCard"]["activeTimeDesc"]
                    jd.address = data["zpData"]["jobCard"]["address"]
                    jd.id = data["zpData"]["jobCard"]["encryptJobId"]
                    jd.salary = data["zpData"]["jobCard"]["salaryDesc"]
                    jd.experience = data["zpData"]["jobCard"]["experienceName"]
                    jd.degree = data["zpData"]["jobCard"]["degreeName"]
                    jd.boss = data["zpData"]["jobCard"]["bossName"]
                    jd.boss_title = data["zpData"]["jobCard"]["bossTitle"]
                    self.update_jd(jd)
                    if self.check_jd(jd, "card"):
                        pass_list.append(url)
            except Exception as e:
                self.handle_exception(e, f",url:{url}")
                continue
        self.conn_commit()
        return pass_list

    def check_dialog(self, cookies_driver: bool = False):
        if cookies_driver:
            original_driver = self.driver
            self.driver = self.cookies_driver
        self.sleep(self.config_setting.sleep)
        if self.is_element_visible("div.dialog-container:last-child"):
            dialog_text = self.get_text("div.dialog-container:last-child")
            if "安全问题" in dialog_text or "沟通" in dialog_text:
                self.click("div.dialog-container:last-child .close")
                self.sleep(self.config_setting.sleep)
        if cookies_driver:
            self.driver = original_driver

    def check_verify(self, cookies_driver: bool = False):
        if cookies_driver:
            original_driver = self.driver
            self.driver = self.cookies_driver
        self.sleep(self.config_setting.sleep_long)
        current_url = self.get_current_url()
        captcha_result = False
        while "safe/verify-slider" in current_url and captcha_result is False:
            print("安全问题")
            try:
                with self.captcha_lock:
                    self.open(self.URL1)
                    time.sleep(self.config_setting.sleep_long)
                    current_url = self.get_current_url()
                    if "safe/verify-slider" not in current_url:
                        break
                    captcha_result = self.captcha()
                    pass
            except (
                NoSuchElementException,
                TimeoutException,
                ElementNotVisibleException,
                HTTPError,
            ) as e:
                self.handle_exception(e)
        time.sleep(self.config_setting.sleep_long)
        if "403.html" in current_url or "error.html" in current_url:
            time.sleep(self.config_setting.timeout)
            print("403或错误")
            sys.exit(1)
        if cookies_driver:
            self.driver = original_driver

    def captcha(self):
        captcha_image_path = self.config_setting.captcha_image_path
        if os.path.exists(captcha_image_path):
            shutil.rmtree(captcha_image_path)
        os.makedirs(captcha_image_path)
        self.open(self.URL13)
        self.click(".btn")
        time.sleep(self.config_setting.sleep_long)
        self.find_element("[class*='geetest_small']")
        element = self.find_element("[class*='geetest_item_wrap']")
        if self.config_setting.download_captcha:
            style_attribute = element.get_attribute("style")
            time.sleep(self.config_setting.sleep_long)
            match = re.search(r"url\(\"(.*?)\"\)", style_attribute)
            if not match:
                return False
            image_url = match.group(1)
            response = httpx.get(image_url)
            with open(captcha_image_path + "/" + "captcha.png", "wb") as file:
                file.write(response.content)
            image = Image.open(captcha_image_path + "/" + "captcha.png")
            width, height = image.size
            top_image = image.crop((0, 0, width, 344))
            top_image.save(captcha_image_path + "/" + "img_image.png")
            bottom_image = image.crop((0, 344, 150, height))
            bottom_image.save(captcha_image_path + "/" + "tip_image.png")
        else:
            self.save_element_as_image_file(
                "[class*='geetest_tip_img']", captcha_image_path + "/" + "tip_image"
            )
            self.save_element_as_image_file(
                "[class*='geetest_item_wrap']", captcha_image_path + "/" + "img_image"
            )
        element_width = element.size["width"]
        element_height = element.size["height"]
        image = cv2.imread(captcha_image_path + "/" + "img_image.png")
        height, width, _ = image.shape
        scale_width = width / element_width
        scale_height = height / element_height
        click_lists = cracker(
            tip_image=captcha_image_path + "/" + "tip_image.png",
            img_image=captcha_image_path + "/" + "img_image.png",
            path=captcha_image_path,
            type=self.config_setting.captcha_distinguish_type,
        )
        img = cv2.imread(captcha_image_path + "/" + "img_image.png")
        for click in click_lists:
            x1, y1, x2, y2 = click
            point = (x1, y1)
            cv2.circle(img, point, radius=10, color=(255, 0, 0), thickness=-1)
            point = (x2, y2)
            cv2.circle(img, point, radius=10, color=(255, 0, 0), thickness=-1)
            self.click_with_offset(
                "[class*='geetest_item_wrap']",
                (x1 + x2) / 2 / scale_width,
                (y1 + y2) / 2 / scale_height,
            )
            time.sleep(self.config_setting.sleep)
        cv2.imwrite(captcha_image_path + "/" + "img_with_point.png", img)
        time.sleep(self.config_setting.sleep)
        self.click(
            "body > div.geetest_panel.geetest_wind > div.geetest_panel_box.geetest_no_logo.geetest_panelshowclick > div.geetest_panel_next > div > div > div.geetest_panel > a"
        )
        time.sleep(self.config_setting.sleep_long)
        try:
            result = self.find_element(
                selector="[class*='geetest_result_tip']",
                timeout=self.config_setting.sleep_long,
            ).text
            return "失败" not in result
        except Exception as e:
            self.handle_exception(e)
            return False

    def process_detail(self, url_list):
        for url in url_list:
            try:
                jd = self.get_jd(self.get_encryptJobId(url))
                self.open(jd.url)
                self.wait_for_element_present("[class*='btn btn-startchat']")
                jd.guide = self.get_text("[class*='pos-bread city-job-guide']")
                if len(jd.guide) > 2:
                    jd.guide = jd.guide[2:]
                jd.scale = self.get_text(".sider-company > p:nth-child(4)")
                if "人" not in jd.scale:
                    jd.scale = ""
                update_text = self.get_text("p.gray")
                if ":" in update_text:
                    jd.update_date = self.parse_update_date(update_text.split(":")[1])
                jd.description = self.get_text(".job-detail-section")
                try:
                    jd.fund = self.get_text("[class*='company-fund']")
                    if len(jd.fund.splitlines()) > 1:
                        jd.fund = jd.fund.splitlines()[-1]
                    res_text = self.get_text(".res-time")
                    if len(res_text.splitlines()) > 1:
                        jd.res = self.parse_res(res_text.splitlines()[-1])
                except Exception as e:
                    self.handle_exception(e, f",url:{url}")
                jd.communicated = self.is_ready_to_communicate(
                    self.get_text("[class*='btn btn-startchat']")
                )
                self.update_jd(jd)
                if self.check_jd(jd, "detail"):
                    self.append_to_file("job.txt", url)
                else:
                    self.append_to_file("detail.txt", url)
            except Exception as e:
                self.append_to_file("detail.txt", url)
                self.handle_exception(e, f",url:{url}")
                self.check_dialog()
                self.check_verify()
                continue
        self.conn_commit()

    def start_chat(self, url: str):
        self.cookies_driver.get(url)
        self.COOKIES_WAIT.until(
            ec.presence_of_element_located(
                (By.CSS_SELECTOR, "[class*='btn btn-startchat']")
            )
        )
        description = self.cookies_driver.find_element(
            By.CLASS_NAME, "job-sec-text"
        ).text
        self.cookies_driver.find_element(
            By.CSS_SELECTOR, "[class*='btn btn-startchat']"
        ).click()
        jd = self.get_jd(self.get_encryptJobId(url))
        jd.communicated = True
        self.update_jd(jd)
        jd.description = description
        try:
            find_element = self.COOKIES_WAIT.until(
                ec.any_of(
                    ec.presence_of_element_located((By.CLASS_NAME, "dialog-con")),
                    ec.presence_of_element_located((By.CSS_SELECTOR, "#chat-input")),
                )
            )
        except Exception as e:
            self.handle_exception(e, f",url:{url}")
            return
        if "chat" in self.cookies_driver.current_url and self.config_setting.chat:
            try:
                self.send_greet_to_chat_box(self.chat.generate_greet(jd))
            except Exception as e:
                self.handle_exception(e, f",url:{url}")
                return
        if "已达上限" in find_element.text:
            sys.exit(0)
        time.sleep(self.config_setting.sleep)

    def send_greet_to_chat_box(self, greet):
        chat_box = self.COOKIES_WAIT.until(
            ec.presence_of_element_located((By.CSS_SELECTOR, "#chat-input"))
        )
        chat_box.clear()
        chat_box.send_keys(greet)
        time.sleep(self.config_setting.sleep)
        self.cookies_driver.find_element(
            By.CSS_SELECTOR,
            "#container > div > div > div.chat-conversation > div.message-controls > div > div.chat-op > button",
        ).click()
        time.sleep(self.config_setting.sleep)

    # pytest zhipinBase.py -m=communicate --env=production --uc --browser=chrome --headed -v -s --junit-xml=junit/test-results.xml
    @pytest.mark.communicate
    def test_communicate(self):
        if not self.env == "production":
            self.driver.quit()
            pytest.skip("need production env to run")
        self.init()
        if os.path.exists("detail.txt"):
            with open("detail.txt", "r") as f:
                urls = f.readlines()
                for url in urls:
                    url = url.strip()
                    try:
                        self.start_chat(url)
                    except Exception as e:
                        self.handle_exception(e, f",url:{url}")
                        self.check_dialog()
                        self.check_verify(cookies_driver=True)
                        continue
        if os.path.exists("job.txt"):
            with open("job.txt", "r") as f:
                urls = f.readlines()
                for url in urls:
                    url = url.strip()
                    try:
                        self.start_chat(url)
                    except Exception as e:
                        self.handle_exception(e, f",url:{url}")
                        self.check_dialog()
                        self.check_verify(cookies_driver=True)
                        continue
