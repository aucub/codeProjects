import datetime
import json
import os
import re
import sys
import time
import sqlite3
import traceback
import requests
from seleniumbase import BaseCase
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from urllib3.exceptions import ProxyError, ConnectTimeoutError, MaxRetryError
from requests.exceptions import ProxyError as requestsProxyError
from rsinfo import RsInfo
from urllib.parse import urlparse, parse_qs
from config import load_config

BaseCase.main(__name__, __file__)

config_setting = load_config()

URL1 = "https://www.zhipin.com/web/geek/job?query="
URL2 = config_setting.query_param + "&salary="
URL3 = "&page="
URL4 = "https://www.zhipin.com/wapi/zpgeek/job/card.json?securityId="
URL5 = "&lid="
URL6 = "&sessionId="
URL7 = "&city="


if len(config_setting.cf_worker) > 0 and not config_setting.cf_worker.isspace():
    # URL1 = URL1.replace("www.zhipin.com", config_setting.cf_worker)
    URL4 = URL4.replace("www.zhipin.com", config_setting.cf_worker)
    print(f"Using {config_setting.cf_worker} as proxy worker")

conn = sqlite3.connect(config_setting.db_path)
cursor = conn.cursor()


class JobQuery(BaseCase):
    def get_proxy(self):
        retries = 10
        retry_delay = 10
        if self.get_proxy_times == config_setting.max_get_proxy_times:
            sys.exit(1)
        self.get_proxy_times += 1
        for i in range(retries):
            try:
                response = requests.get("https://proxypool-vwc3.onrender.com/random")
                response.raise_for_status()
                print(f"Got proxy: {response.text}")
                return response.text
            except Exception as e:
                print(f"An error occurred: {e}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
        return None

    def set_proxy(self):
        env_proxy = os.getenv("HTTP_PROXY")
        self.proxy_str = self.get_proxy()
        self.requests_proxies = None
        if not env_proxy:
            self.requests_proxies = {
                "http": "http://{}".format(self.proxy_str),
                "https": "http://{}".format(self.proxy_str),
            }

    def append_to_file(self, file_path, line_to_append):
        with open(file_path, "a", encoding="utf-8", newline="") as file:
            file.write(f"{line_to_append}\n")

    def test_query(self):
        self.get_proxy_times = 0
        self.set_default_timeout(config_setting.timeout)
        # self.set_proxy()
        wheels = self.load_state() or [[], [], [], 0]
        self.requests_headers = {
            "User-Agent": self.execute_script("return navigator.userAgent;"),
        }
        for city in config_setting.query_city_list:
            if city in wheels[0]:
                continue
            for query in config_setting.query_list:
                if query in wheels[1]:
                    continue
                for salary in config_setting.salary_list:
                    if salary in wheels[2]:
                        continue
                    for page in range(config_setting.page_min, config_setting.page_max):
                        if page <= wheels[3]:
                            continue
                        try:
                            self.query_and_process_jobs(
                                URL1
                                + query
                                + URL7
                                + city
                                + URL2
                                + salary
                                + URL3
                                + str(page)
                            )
                        except (TimeoutException, StaleElementReferenceException):
                            traceback.print_exc()
                            continue
                        wheels[3] = page
                        self.save_state(wheels)
                    wheels[3] = 0
                    wheels[2].append(salary)
                    self.save_state(wheels)
                wheels[2] = []
                wheels[1].append(query)
                self.save_state(wheels)
            wheels[1] = []
            wheels[0].append(city)
            self.save_state(wheels)
        wheels[0] = []
        self.save_state(wheels)

    def query_and_process_jobs(self, page_url):
        self.open(page_url)
        self.check_dialog()
        self.check_verify()
        try:
            self.wait_for_element_present(
                ".job-card-wrapper", timeout=config_setting.timeout
            )
            find_element_list = self.find_elements("[class*='job-card-wrapper']")
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
            rsinfo = RsInfo()
            job_info = job_element.find_element(
                By.CSS_SELECTOR, "div.job-info.clearfix"
            )
            job_info_html = job_info.get_attribute(
                "innerHTML",
            )
            if self.is_ready_to_communicate(job_info_html):
                rsinfo.communicate = "立即沟通"
            else:
                rsinfo.communicate = "继续沟通"
            url = job_element.find_element(
                By.CSS_SELECTOR, " .job-card-left"
            ).get_attribute("href")
            id = self.get_encryptJobId(url)
            row = self.get_rsinfo(id)
            if row and row.id == id:
                if config_setting.skip_known:
                    self.sleep(config_setting.sleep)
                    continue
                else:
                    rsinfo = row
            rsinfo.url = url.split("&securityId")[0]
            rsinfo.name = job_element.find_element(By.CSS_SELECTOR, " .job-name").text
            rsinfo.city = job_element.find_element(By.CSS_SELECTOR, " .job-area").text
            rsinfo.company = job_element.find_element(
                By.CSS_SELECTOR, " .company-name a"
            ).text
            rsinfo.industry = job_element.find_element(
                By.CSS_SELECTOR, " .company-tag-list li"
            ).text
            rsinfo.datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            rsinfo.id = id
            self.update_rsinfo(rsinfo)
            if self.check_rsinfo(rsinfo, "query"):
                url_list.append(url)
            conn.commit()
            self.url_list_process(url_list)

    def check_dialog(self):
        self.sleep(config_setting.sleep)
        if self.is_element_visible("div.dialog-container:last-child"):
            dialog_text = self.get_text("div.dialog-container:last-child")
            if "安全问题" in dialog_text or "沟通" in dialog_text:
                self.click("div.dialog-container:last-child .close")
                self.sleep(config_setting.sleep)

    def check_verify(self):
        try:
            time.sleep(config_setting.sleep)
            current_url = self.get_current_url()
            if "safe/verify-slider" in current_url:
                time.sleep(config_setting.timeout)
                print("安全问题")
                # sys.exit(1)
            time.sleep(config_setting.sleep)
            if "403.html" in current_url or "error.html" in current_url:
                time.sleep(config_setting.timeout)
                print("403或错误")
                # sys.exit(1)
        except Exception:
            tb_str = traceback.format_exc()
            self.append_to_file("log.txt", f"异常信息：{tb_str}")

    def check_card(self, url: str):
        query_params = parse_qs(urlparse(url).query)
        lid = query_params.get("lid", [None])[0]
        security_id = query_params.get("securityId", [None])[0]
        try:
            retry_count = 5
            while retry_count > 0:
                try:
                    response = requests.get(
                        URL4 + security_id + URL5 + lid + URL6,
                        headers=self.requests_headers,
                        #  proxies=self.requests_proxies,
                    )
                    retry_count = 0
                    print(response.text)
                    print(response.url)
                except Exception:
                    traceback.print_exc()
                    retry_count -= 1
                    if retry_count == 0:
                        # self.set_proxy()
                        traceback.print_exc()
                        tb_str = traceback.format_exc()
                        self.append_to_file(
                            "log.txt", f"异常信息：{tb_str}，url：{url}"
                        )
            if response.status_code == 200:
                data = response.json()
            if data["message"] == "Success":
                rsinfo = self.get_rsinfo(self.get_encryptJobId(url))
                rsinfo.url = url.split("&securityId")[0]
                rsinfo.description = data["zpData"]["jobCard"]["postDescription"]
                rsinfo.active = data["zpData"]["jobCard"]["activeTimeDesc"]
                rsinfo.address = data["zpData"]["jobCard"]["address"]
                rsinfo.id = data["zpData"]["jobCard"]["encryptJobId"]
                rsinfo.salary = data["zpData"]["jobCard"]["salaryDesc"]
                rsinfo.experience = data["zpData"]["jobCard"]["experienceName"]
                rsinfo.degree = data["zpData"]["jobCard"]["degreeName"]
                rsinfo.boss = data["zpData"]["jobCard"]["bossName"]
                rsinfo.boss_title = data["zpData"]["jobCard"]["bossTitle"]
                self.update_rsinfo(rsinfo)
                return self.check_rsinfo(rsinfo, "card")
            else:
                return True
        except (ProxyError, ConnectTimeoutError, MaxRetryError, requestsProxyError):
            traceback.print_exc()
            # self.set_proxy()
            tb_str = traceback.format_exc()
            self.append_to_file("log.txt", f"异常信息：{tb_str}，url：{url}")
        except Exception:
            traceback.print_exc()
            tb_str = traceback.format_exc()
            self.append_to_file("log.txt", f"异常信息：{tb_str}，url：{url}")

    def url_list_process(self, url_list):
        url_list = self.check_url_list(url_list)
        conn.commit()
        self.detail(url_list)
        conn.commit()

    def check_url_list(self, url_list):
        card_url_list = []
        for url in url_list:
            if self.check_card(url):
                card_url_list.append(url)
        return card_url_list

    def detail(self, url_list):
        for url in url_list:
            try:
                self.open(url)
                self.check_verify()
                self.wait_for_element_present("[class*='btn btn-startchat']")
                self.check_dialog()
                rsinfo = self.get_rsinfo(self.get_encryptJobId(url))
                rsinfo.guide = self.get_text("[class*='pos-bread city-job-guide']")
                if len(rsinfo.guide) > 2:
                    rsinfo.guide = rsinfo.guide[2:]
                rsinfo.scale = self.get_text(".sider-company > p:nth-child(4)")
                if "人" not in rsinfo.scale:
                    rsinfo.scale = ""
                rsinfo.update_date = self.get_text("p.gray")
                if len(rsinfo.update_date) > 4:
                    rsinfo.update_date = rsinfo.update_date[4:]
                rsinfo.description = self.get_text(".job-detail-section")
                try:
                    rsinfo.fund = self.get_text("[class*='company-fund']")
                    if len(rsinfo.fund.splitlines()) > 1:
                        rsinfo.fund = rsinfo.fund.splitlines()[-1]
                    rsinfo.res = self.get_text(".res-time")
                    if len(rsinfo.res.splitlines()) > 1:
                        rsinfo.res = rsinfo.res.splitlines()[-1]
                except Exception:
                    traceback.print_exc()
                    tb_str = traceback.format_exc()
                    self.append_to_file(
                        "log.txt",
                        f"在提取详细信息时遇到异常，异常信息：{tb_str}，url：{url}",
                    )
                    continue
                rsinfo.communicate = self.get_text("[class*='btn btn-startchat']")
                self.update_rsinfo(rsinfo)
                if not self.check_rsinfo(rsinfo, "detail"):
                    print(f"未处理：\n{url}")
                    self.append_to_file("detail.txt", url)
                    continue
                self.append_to_file("job.txt", url)
                print(f"已处理：\n{url}")
            except Exception:
                traceback.print_exc()
                print(f"异常：\n{url}")
                self.append_to_file("job.txt", url)
                tb_str = traceback.format_exc()
                self.append_to_file(
                    "log.txt",
                    f"在处理详细信息时遇到异常，异常信息：{tb_str}，url：{url}",
                )
                continue

    def check_rsinfo(slef, rsinfo: RsInfo, stage: str):
        if stage == "query":
            return (
                slef.is_ready_to_communicate(rsinfo.communicate)
                and slef.check_name(rsinfo.name)
                and slef.check_city(rsinfo.city)
                and slef.check_company(rsinfo.company)
                and slef.check_industry(rsinfo.industry)
            )
        elif stage == "card":
            return (
                slef.check_description(rsinfo.description)
                and slef.check_active(rsinfo.active)
                and slef.check_city(rsinfo.address)
                and slef.check_salary(rsinfo.salary)
                and slef.check_experience(rsinfo.experience)
                and slef.check_degree(rsinfo.degree)
                and slef.check_boss_title(rsinfo.boss_title)
            )
        elif stage == "detail":
            return (
                slef.check_guide(rsinfo.guide)
                and slef.check_scale(rsinfo.scale)
                and slef.check_res(rsinfo.res)
                and slef.check_update(rsinfo.update_date)
                and slef.check_description(rsinfo.description)
                and slef.check_offline(rsinfo.description, rsinfo.city)
                and slef.check_fund(rsinfo.fund)
                and slef.is_ready_to_communicate(rsinfo.communicate)
            )

    def update_rsinfo(self, rsinfo):
        if len(rsinfo.id) == 0 or rsinfo.id.isspace():
            return
        cursor.execute("SELECT * FROM rsinfo WHERE id = ?", (rsinfo.id,))
        row = cursor.fetchone()
        if row:
            cursor.execute(
                "UPDATE rsinfo SET url=?, name=?, city=?, address=?,    guide=?, scale=?, update_date=?, salary=?,     experience=?, degree=?, company=?, industry=?,  fund=?, res=?, boss=?, boss_title=?, active=?,   description=?, communicate=?, datetime=? WHERE id=?",
                (
                    rsinfo.url,
                    rsinfo.name,
                    rsinfo.city,
                    rsinfo.address,
                    rsinfo.guide,
                    rsinfo.scale,
                    rsinfo.update_date,
                    rsinfo.salary,
                    rsinfo.experience,
                    rsinfo.degree,
                    rsinfo.company,
                    rsinfo.industry,
                    rsinfo.fund,
                    rsinfo.res,
                    rsinfo.boss,
                    rsinfo.boss_title,
                    rsinfo.active,
                    rsinfo.description,
                    rsinfo.communicate,
                    rsinfo.datetime,
                    rsinfo.id,
                ),
            )
        else:
            cursor.execute(
                "INSERT INTO rsinfo (url, id, name, city, address,  guide, scale, update_date, salary, experience,   degree, company, industry, fund, res, boss,   boss_title, active, description, communicate,     datetime) VALUES        (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?  , ?, ?, ?)",
                (
                    rsinfo.url,
                    rsinfo.id,
                    rsinfo.name,
                    rsinfo.city,
                    rsinfo.address,
                    rsinfo.guide,
                    rsinfo.scale,
                    rsinfo.update_date,
                    rsinfo.salary,
                    rsinfo.experience,
                    rsinfo.degree,
                    rsinfo.company,
                    rsinfo.industry,
                    rsinfo.fund,
                    rsinfo.res,
                    rsinfo.boss,
                    rsinfo.boss_title,
                    rsinfo.active,
                    rsinfo.description,
                    rsinfo.communicate,
                    rsinfo.datetime,
                ),
            )

    def get_rsinfo(self, id):
        cursor.execute("SELECT * FROM rsinfo WHERE id = ?", (id,))
        row = cursor.fetchone()
        if row:
            return RsInfo(*row)
        else:
            return RsInfo()

    def get_encryptJobId(self, url):
        match = re.search(r"/+([^/]+)\.html", url)
        if match:
            return match.group(1)
        else:
            return ""

    def check_active(self, active_text):
        """
        检查活跃时间
        """
        return all(item not in active_text for item in config_setting.active_block_list)

    def check_scale(self, scale_text):
        """
        检查规模
        """
        return all(item not in scale_text for item in config_setting.scale_block_list)

    def check_experience(self, experience_text):
        """
        检查经验
        """
        return all(
            item not in experience_text for item in config_setting.experience_block_list
        )

    def check_degree(self, degree_text):
        """
        检查学位
        """
        return all(item not in degree_text for item in config_setting.degree_block_list)

    def check_fund(self, fund_text):
        """
        检查资金
        """
        if "-" in fund_text:
            return False
        if "万" in fund_text:
            fund_text = fund_text[:-3]
            numbers = re.findall(r"\d+\.\d+|\d+", fund_text)
            numbers = list(map(float, numbers))
            return numbers[0] > config_setting.fund_min
        return True

    def check_salary(self, salary_text):
        """
        检查薪资
        """
        pattern = r"(\d+)-(\d+)K"
        match = re.search(pattern, salary_text)
        if match:
            low_salary = int(match.group(1))
            return low_salary < config_setting.salary_max

    def check_description(self, description_text):
        """
        检查职位描述
        """
        if len(description_text) < config_setting.description_min:
            return False
        description_text = description_text.lower()
        if all(
            item not in description_text
            for item in config_setting.description_keyword_list
        ):
            return False
        if any(
            item in description_text for item in config_setting.description_block_list
        ):
            return False
        if "截止日期" in description_text:
            exp_date_text = description_text[
                description_text.index("截止日期") + 5 : description_text.index(
                    "截止日期"
                )
                + 15
            ]
            date_format = "%Y.%m.%d"
            try:
                if time.mktime(time.strptime(exp_date_text, date_format)) < time.time():
                    return False
            except Exception:
                pass
            description_text = (
                description_text[: description_text.index("截止日期 ")]
                + description_text[description_text.index("截止日期 ") + 15 :]
            )
        if config_setting.graduate != 0:
            graduate = config_setting.graduate
            if "毕业时间" in description_text:
                graduation_time = description_text[
                    description_text.index("毕业时间") : description_text.index(
                        "毕业时间"
                    )
                    + 15
                ]
                graduation_time_min_block = str(graduate + 1) + "年-"
                graduation_time_block_list = [
                    "20" + str(graduate - 3),
                    "20" + str(graduate - 2),
                    "20" + str(graduate - 1),
                ]
                graduation_times = ["不限", str(graduate)]
                graduation_times_max_list = [
                    "-20" + str(graduate + 2),
                    "-20" + str(graduate + 1),
                ]
                if any(item in graduation_time for item in graduation_times):
                    return True
                if graduation_time_min_block in graduation_time:
                    return False
                if any(item in graduation_time for item in graduation_times_max_list):
                    return True
                if any(item in graduation_time for item in graduation_time_block_list):
                    return False
            graduations_experiences = [
                str(graduate) + "届",
                str(graduate) + "年",
                str(graduate + 1) + "年及之前",
                "往届",
                "0-",
                "0～",
                "0~",
            ]
            if any(item in description_text for item in graduations_experiences):
                return True
            graduations_max = [
                str(graduate + 1) + "届",
                str(graduate + 1) + "年",
                str(graduate + 1) + "应届",
            ]
            if any(item in description_text for item in graduations_max):
                return str(graduate) in description_text
            graduations = ["应届" "毕业生" "实习生" "无经验"]
            if any(item in description_text for item in graduations):
                return True
        return all(
            item not in description_text
            for item in config_setting.description_experience_block_list
        )

    def check_res(self, res_text):
        """
        检查成立时间
        """
        try:
            res_text = res_text[-10:]
            date_format = "%Y-%m-%d"
            return time.mktime(time.strptime(res_text, date_format)) < (
                time.time() - config_setting.res
            )
        except Exception:
            return True

    def check_update(self, update_text):
        """
        检查更新日期
        """
        try:
            update_text = update_text[-10:]
            date_format = "%Y-%m-%d"
            return time.mktime(time.strptime(update_text, date_format)) > (
                time.time() - config_setting.update
            )
        except Exception:
            return True

    def is_ready_to_communicate(self, startchat_text):
        """
        检查能否沟通
        """
        return "立即" in startchat_text

    def check_city(self, city_text):
        """
        检查城市
        """
        try:
            return all(item not in city_text for item in config_setting.city_block_list)
        except Exception:
            return True

    def check_boss_title(self, boss_title_text: str):
        """
        检查人事
        """
        boss_title_text = boss_title_text.lower()
        return all(
            item not in boss_title_text for item in config_setting.boss_title_block_list
        )

    def check_offline(self, description_text, city_text):
        """
        检查面试方式
        """
        offlines = [
            "不支持在线",
            "不支持线上",
            "线下面试",
            "线下笔试",
            "现场面试",
            "现场机考",
            "不接受线上",
            "未开放线上",
            "现场coding",
            "附近优先",
        ]
        if config_setting.offline_interview:
            if any(item in description_text for item in offlines):
                return any(
                    item in city_text for item in config_setting.offline_city_list
                )
        return True

    def check_industry(self, industry_text):
        """
        检查行业
        """
        return all(
            item not in industry_text for item in config_setting.industry_block_list
        )

    def check_name(self, name_text: str):
        """
        检查标题
        """
        name_text = name_text.lower()
        return all(item not in name_text for item in config_setting.name_block_list)

    def check_guide(self, guide_text: str):
        """
        检查导航
        """
        guide_text = guide_text.lower()
        return all(item not in guide_text for item in config_setting.guide_block_list)

    def check_company(self, company_text):
        """
        检查公司名称
        """
        return all(
            item not in company_text for item in config_setting.company_block_list
        )

    def save_state(self, wheels):
        with open(
            "state.json",
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(wheels, f, ensure_ascii=False)
        print(f"保存state.json成功{wheels}")

    def load_state(self):
        try:
            env_state = os.getenv("STATE")
            if env_state:
                print(f"从环境变量获取state.json成功{env_state}")
                with open(
                    "state.json",
                    "w",
                    encoding="utf-8",
                ) as f:
                    f.write(env_state)
                return json.load(env_state)
            with open(
                "state.json",
                "r",
                encoding="utf-8",
            ) as f:
                return json.load(f)
        except (FileNotFoundError, Exception):
            return None
