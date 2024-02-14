import datetime
import json
import sys
import time
import traceback
from urllib.parse import parse_qs, urlparse
from zhipin import ZhiPin
from seleniumbase import BaseCase
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from jd import JD

BaseCase.main(__name__, __file__)


class ZhiPinBase(BaseCase, ZhiPin):
    def init(self):
        self.set_cookies()
        self.wheels = self.load_state()
        self.set_cf_worker()
        self.set_proxy()

    def set_cookies(self):
        if self.config_setting.cookies_path:
            self.open(self.URL1)
            self.load_cookies(self.config_setting.cookies_path)

    def get_cookies(self):
        if self.config_setting.cookies_path:
            self.get_new_driver(self.config_setting.user_data_dir)
            time.sleep(self.config_setting.timeout)
            self.open(self.URL1)
            self.save_cookies(self.config_setting.cookies_path)

    def test_query(self):
        self.init()
        self.set_default_timeout(self.config_setting.timeout)
        self.requests_headers = {
            "User-Agent": self.execute_script("return navigator.userAgent;"),
        }
        for city in self.config_setting.query_city_list:
            if city in self.wheels[0]:
                continue
            for query in self.config_setting.query_list:
                if query in self.wheels[1]:
                    continue
                for salary in self.config_setting.salary_list:
                    if salary in self.wheels[2]:
                        continue
                    for page in range(
                        self.config_setting.page_min, self.config_setting.page_max
                    ):
                        if page <= self.wheels[3]:
                            continue
                        try:
                            self.query_and_process_jobs_Base(
                                self.URL1
                                + query
                                + self.URL7
                                + city
                                + self.URL2
                                + salary
                                + self.URL3
                                + str(page)
                            )
                            # self.query_and_process_jobs(
                            #     self.URL12
                            #     + query
                            #     + self.URL7
                            #     + city
                            #     + self.URL2
                            #     + salary
                            #     + self.URL3
                            #     + str(page)
                            # )
                        except (TimeoutException, StaleElementReferenceException):
                            traceback.print_exc()
                            continue
                        self.wheels[3] = page
                        self.save_state(self.wheels)
                    self.wheels[3] = 0
                    self.wheels[2].append(salary)
                    self.save_state(self.wheels)
                self.wheels[2] = []
                self.wheels[1].append(query)
                self.save_state(self.wheels)
            self.wheels[1] = []
            self.wheels[0].append(city)
            self.save_state(self.wheels)
        self.wheels[0] = []
        self.save_state(self.wheels)
        self.cursor.close()
        self.conn.close()

    def query_and_process_jobs_Base(self, page_url):
        self.open(page_url)
        try:
            self.wait_for_element_present(".job-card-wrapper")
            find_element_list = self.find_elements(".job-card-wrapper")
        except TimeoutException:
            return 1
        except Exception:
            traceback.print_exc()
            self.check_dialog()
            self.check_verify()
            tb_str = traceback.format_exc()
            self.append_to_file("log.txt", f"异常信息：{tb_str}，page_url：{page_url}")
            return 1
        url_list = []
        for job_element in find_element_list:
            job_element: WebElement
            try:
                jd = JD()
                job_info = job_element.find_element(
                    value="[class*='job-info clearfix']", by=By.CSS_SELECTOR
                )
                job_info_html = job_info.get_attribute(
                    "innerHTML",
                )
                jd.communicated = not self.is_ready_to_communicate(job_info_html)
                url = job_element.find_element(
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
                jd.name = job_element.find_element(
                    value=" .job-name", by=By.CSS_SELECTOR
                ).text
                jd.city = job_element.find_element(
                    value=" .job-area", by=By.CSS_SELECTOR
                ).text
                jd.company = job_element.find_element(
                    value=" .company-name a", by=By.CSS_SELECTOR
                ).text
                jd.industry = job_element.find_element(
                    value=" .company-tag-list    li", by=By.CSS_SELECTOR
                ).text
                jd.checked_date = datetime.datetime.now()
                jd.id = id
                print(jd)
                self.update_jd(jd)
                if self.check_jd(jd, "query"):
                    url_list.append(url)
            except Exception:
                traceback.print_exc()
                tb_str = traceback.format_exc()
                self.append_to_file(
                    "log.txt", f"异常信息：{tb_str}，page_url：{page_url}"
                )
                continue
        self.conn.commit()
        self.url_list_process(url_list)

    def check_card(self, url: str):
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
                return self.check_jd(jd, "card")
        except Exception:
            traceback.print_exc()
            tb_str = traceback.format_exc()
            self.append_to_file("log.txt", f"异常信息：{tb_str}，url：{url}")
            return True

    def check_dialog(self):
        self.sleep(self.config_setting.sleep)
        if self.is_element_visible("div.dialog-container:last-child"):
            dialog_text = self.get_text("div.dialog-container:last-child")
            if "安全问题" in dialog_text or "沟通" in dialog_text:
                self.click("div.dialog-container:last-child .close")
                self.sleep(self.config_setting.sleep)

    def check_verify(self):
        try:
            time.sleep(self.config_setting.sleep)
            current_url = self.get_current_url()
            if "safe/verify-slider" in current_url:
                time.sleep(self.config_setting.timeout)
                print("安全问题")
                if self.headless_active:
                    sys.exit(1)
            time.sleep(self.config_setting.sleep)
            if "403.html" in current_url or "error.html" in current_url:
                time.sleep(self.config_setting.timeout)
                print("403或错误")
                if self.headless_active:
                    sys.exit(1)
        except Exception:
            tb_str = traceback.format_exc()
            self.append_to_file("log.txt", f"异常信息：{tb_str}")

    def url_list_process(self, url_list):
        url_list = self.check_url_list(url_list)
        self.conn.commit()
        self.detail(url_list)
        self.conn.commit()

    def check_url_list(self, url_list):
        card_url_list = []
        for url in url_list:
            if self.check_card(url):
                card_url_list.append(url)
        return card_url_list

    def detail(self, url_list):
        for url in url_list:
            try:
                jd = self.get_jd(self.get_encryptJobId(url))
                self.open(jd.url)
                self.wait_for_element_present("[class*='btn btn-startchat']")
                self.check_dialog()
                jd.guide = self.get_text("[class*='pos-bread city-job-guide']")
                if len(jd.guide) > 2:
                    jd.guide = jd.guide[2:]
                jd.scale = self.get_text(".sider-company > p:nth-child(4)")
                if "人" not in jd.scale:
                    jd.scale = ""
                update_text = self.get_text("p.gray")
                if len(update_text) > 4:
                    jd.update_date = self.parse_update_date(update_text[4:])
                jd.description = self.get_text(".job-detail-section")
                try:
                    jd.fund = self.get_text("[class*='company-fund']")
                    if len(jd.fund.splitlines()) > 1:
                        jd.fund = jd.fund.splitlines()[-1]
                    res_text = self.get_text(".res-time")
                    if len(res_text.splitlines()) > 1:
                        jd.res = self.parse_res(res_text.splitlines()[-1])
                except Exception:
                    traceback.print_exc()
                    tb_str = traceback.format_exc()
                    self.append_to_file(
                        "log.txt",
                        f"在提取详细信息时遇到异常，异常信息：{tb_str}，url：{url}",
                    )
                    continue
                jd.communicated = self.is_ready_to_communicate(
                    self.get_text("[class*='btn btn-startchat']")
                )
                self.update_jd(jd)
                if not self.check_jd(jd, "detail"):
                    self.append_to_file("detail.txt", url)
                    continue
                self.append_to_file("job.txt", url)
            except Exception:
                self.check_verify()
                traceback.print_exc()
                self.append_to_file("job.txt", url)
                tb_str = traceback.format_exc()
                self.append_to_file(
                    "log.txt",
                    f"在处理详细信息时遇到异常，异常信息：{tb_str}，url：{url}",
                )
                continue
