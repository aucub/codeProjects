import atexit
import datetime
import json
import os
import re
import time
import traceback
import httpx
import mysql.connector
from _mysql_connector import MySQLInterfaceError
from jd import JD
from urllib.parse import urlparse, parse_qs
from config import load_config
from dotenv import load_dotenv

load_dotenv()


class VerifyException(Exception):
    """验证异常"""

    def __init__(self, message=None):
        self.message = message


class ZhiPin:
    config_setting = load_config()
    URL1 = "https://www.zhipin.com/web/geek/job?query="
    URL2 = config_setting.query_param + "&salary="
    URL3 = "&page="
    URL4 = "https://www.zhipin.com/wapi/zpgeek/job/card.json?securityId="
    URL5 = "&lid="
    URL6 = "&sessionId="
    URL7 = "&city="
    URL8 = "https://www.zhipin.com/job_detail/"
    URL9 = ".html"
    URL10 = "?lid="
    URL11 = "&securityId="
    URL12 = "https://www.zhipin.com/wapi/zpgeek/search/joblist.json?scene=1&payType=&partTime=&stage=&jobType=&multiBusinessDistrict=&multiSubway=&pageSize=30&query="
    URL13 = "https://www.zhipin.com/web/user/safe/verify-slider"
    db_url = urlparse(os.getenv("DB_URL"))
    db_string = parse_qs(db_url.query)
    conn = mysql.connector.connect(
        host=db_url.hostname,
        port=db_url.port if db_url.port else 3306,
        user=db_string["user"][0],
        password=db_string["password"][0],
        database=db_url.path[1:],
    )
    cursor = conn.cursor()

    def cleanup(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def __init__(self) -> None:
        atexit.register(self.cleanup)
        self.wheels = self.load_state()
        self.set_proxy()

    def set_proxy(self):
        os.environ["all_proxy"] = ""
        os.environ["ALL_PROXY"] = ""
        env_proxy = os.getenv("PROXY_URL")
        self.proxies = None
        if env_proxy:
            self.proxy_str = env_proxy
            self.proxies = {
                "http://": self.proxy_str,
                "https://": self.proxy_str,
            }

    def append_to_file(self, file_path, line_to_append):
        with open(file_path, "a", encoding="utf-8", newline="") as file:
            file.write(f"{line_to_append}\n")

    def iterate_job_parameters(self):
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
                        self.execute_find_jobs(city, query, salary, page)
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

    def query_jobs(self, page_url):
        url_list = []
        try:
            response = httpx.get(
                url=page_url,
                proxies=self.proxies,
            )
            if response.status_code != 200:
                raise Exception(response.text)
            else:
                print(response.text)
                data = response.json()
        except Exception as e:
            self.handle_exception(e, f"，page_url：{page_url}")
            return url_list
        if data["message"] == "Success":
            jobList = data["zpData"]["jobList"]
            for job in jobList:
                try:
                    jd = JD()
                    jd.id = job["encryptJobId"]
                    jd.communicated = not job["contact"]
                    row = self.get_jd(jd.id)
                    if row and row.id == jd.id:
                        if self.config_setting.skip_known:
                            time.sleep(self.config_setting.sleep)
                            continue
                        else:
                            jd = row
                    jd.url = self.URL8 + jd.id + self.URL9
                    jd.name = job["jobName"]
                    jd.city = job["cityName"]
                    jd.company = job["brandName"]
                    jd.industry = job["brandIndustry"]
                    jd.scale = job["brandScaleName"]
                    jd.address = (
                        job["cityName"] + job["areaDistrict"] + job["businessDistrict"]
                    )
                    jd.experience = job["jobExperience"]
                    jd.degree = job["jobDegree"]
                    jd.salary = job["salaryDesc"]
                    jd.boss = job["bossName"]
                    jd.boss_title = job["bossTitle"]
                    jd.update_date = datetime.datetime.fromtimestamp(
                        job["lastModifyTime"] / 1000
                    )
                    jd.checked_date = datetime.datetime.now()
                    jd.level = "list"
                    self.update_jd(jd)
                    if self.check_jd(jd, "query"):
                        url_list.append(
                            jd.url
                            + self.URL10
                            + data["zpData"]["lid"]
                            + self.URL11
                            + job["securityId"]
                            + self.URL6
                        )
                except Exception as e:
                    self.handle_exception(e, f"，page_url：{page_url}")
                    continue
            self.conn_commit()
        return url_list

    def check_card(self, url_list: list):
        pass_list = []
        for url in url_list:
            query_params = parse_qs(urlparse(url).query)
            lid = query_params.get("lid", [None])[0]
            security_id = query_params.get("securityId", [None])[0]
            try:
                response = httpx.get(
                    self.URL4 + security_id + self.URL5 + lid + self.URL6,
                    proxies=self.proxies,
                )
                if response.status_code != 200:
                    raise Exception(response.text)
                else:
                    data = response.json()
                    print(data)
                if data["message"] == "Success":
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
                    jd.level = "card"
                    self.update_jd(jd)
                    if self.check_jd(jd, "card"):
                        pass_list.append(url)
            except Exception as e:
                self.handle_exception(e, f"，url：{url}")
                continue
        self.conn_commit()
        return pass_list

    def check_jd(slef, jd: JD, stage: str):
        if stage == "query":
            return (
                not jd.communicated
                and slef.check_name(jd.name)
                and slef.check_city(jd.city)
                and slef.check_company(jd.company)
                and slef.check_industry(jd.industry)
            )
        elif stage == "card":
            return (
                slef.check_description(jd.description)
                and slef.check_active(jd.active)
                and slef.check_city(jd.address)
                and slef.check_salary(jd.salary)
                and slef.check_experience(jd.experience)
                and slef.check_degree(jd.degree)
                and slef.check_boss_title(jd.boss_title)
            )
        elif stage == "detail":
            return (
                slef.check_guide(jd.guide)
                and slef.check_scale(jd.scale)
                and slef.check_res(jd.res)
                and slef.check_update_date(jd.update_date)
                and slef.check_description(jd.description)
                and slef.check_offline(jd.description, jd.city)
                and slef.check_fund(jd.fund)
                and not jd.communicated
            )

    def update_jd(self, jd: JD):
        if not jd.id:
            return
        try:
            self.cursor.execute("SELECT * FROM jd WHERE id = %s", (jd.id,))
            row = self.cursor.fetchone()
            if row:
                self.cursor.execute(
                    "UPDATE jd SET url=%s, name=%s, city=%s, address=%s, guide=%s, scale=%s, update_date=%s,    salary=%s, experience=%s, degree=%s, company=%s, industry=%s, fund=%s, res=%s, boss=%s,    boss_title=%s, active=%s, description=%s, communicated=%s, checked_date=%s,  level=%s WHERE id=%s",
                    (
                        jd.url,
                        jd.name,
                        jd.city,
                        jd.address,
                        jd.guide,
                        jd.scale,
                        self.format_date(jd.update_date),
                        jd.salary,
                        jd.experience,
                        jd.degree,
                        jd.company,
                        jd.industry,
                        jd.fund,
                        self.format_date(jd.res),
                        jd.boss,
                        jd.boss_title,
                        jd.active,
                        jd.description,
                        int(jd.communicated),
                        self.format_datetime(jd.checked_date),
                        jd.level,
                        jd.id,
                    ),
                )
            else:
                self.cursor.execute(
                    "INSERT IGNORE INTO jd (url, id, name, city, address, guide, scale, update_date, salary, experience, degree, company, industry, fund, res, boss, boss_title, active, description, communicated, checked_date,  level) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (
                        jd.url,
                        jd.id,
                        jd.name,
                        jd.city,
                        jd.address,
                        jd.guide,
                        jd.scale,
                        self.format_date(jd.update_date),
                        jd.salary,
                        jd.experience,
                        jd.degree,
                        jd.company,
                        jd.industry,
                        jd.fund,
                        self.format_date(jd.res),
                        jd.boss,
                        jd.boss_title,
                        jd.active,
                        jd.description,
                        int(jd.communicated),
                        self.format_datetime(jd.checked_date),
                        jd.level,
                    ),
                )
        except (mysql.connector.errors.Error, MySQLInterfaceError) as e:
            self.conn.reconnect()
            self.handle_exception(e, f"，id：{jd.id}")

    def conn_commit(self):
        try:
            self.conn.commit()
        except (mysql.connector.errors.Error, MySQLInterfaceError) as e:
            self.conn.reconnect()
            self.handle_exception(e)

    def get_jd(self, id):
        try:
            self.cursor.execute("SELECT * FROM jd WHERE id = %s", (id,))
            row = self.cursor.fetchone()
            if row:
                return JD(*row)
            else:
                return JD()
        except (mysql.connector.errors.Error, MySQLInterfaceError) as e:
            self.conn.reconnect()
            self.handle_exception(e, f"，id：{id}")

    def get_jd_url_list(self, level: str):
        try:
            self.cursor.execute(
                "SELECT url FROM jd WHERE level = %s AND communicated = 0", (level,)
            )
            rows = self.cursor.fetchall()
            if rows:
                return [row[0] for row in rows]
            else:
                return []
        except (mysql.connector.errors.Error, MySQLInterfaceError) as e:
            self.conn.reconnect()
            self.handle_exception(e, f"，level：{level}")

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
        return all(
            item not in active_text for item in self.config_setting.active_block_list
        )

    def check_scale(self, scale_text):
        """
        检查规模
        """
        return all(
            item not in scale_text for item in self.config_setting.scale_block_list
        )

    def check_experience(self, experience_text):
        """
        检查经验
        """
        return all(
            item not in experience_text
            for item in self.config_setting.experience_block_list
        )

    def check_degree(self, degree_text):
        """
        检查学位
        """
        return all(
            item not in degree_text for item in self.config_setting.degree_block_list
        )

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
            return numbers[0] > self.config_setting.fund_min
        return True

    def check_salary(self, salary_text):
        """
        检查薪资
        """
        pattern = r"(\d+)-(\d+)K"
        match = re.search(pattern, salary_text)
        if match:
            low_salary = int(match.group(1))
            return low_salary < self.config_setting.salary_max

    def check_description(self, description_text: str):
        """
        检查职位描述
        """
        if len(description_text) < self.config_setting.description_min:
            return False
        description_text = description_text.lower()
        if all(
            item not in description_text
            for item in self.config_setting.description_keyword_list
        ):
            return False
        if any(
            item in description_text
            for item in self.config_setting.description_block_list
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
            except Exception as e:
                self.handle_exception(e)
                pass
            description_text = (
                description_text[: description_text.index("截止日期")]
                + description_text[description_text.index("截止日期") + 15 :]
            )
        if self.config_setting.graduate != 0:
            graduate = self.config_setting.graduate
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
            for item in self.config_setting.description_experience_block_list
        )

    def parse_res(self, res_text):
        try:
            date_format = "%Y-%m-%d"
            return datetime.datetime.strptime(res_text, date_format).date()
        except Exception as e:
            self.handle_exception(e, res_text)
            return None

    def format_date(self, formatted_date: datetime.date):
        try:
            if formatted_date is None:
                return None
            return formatted_date.strftime("%Y-%m-%d")
        except Exception as e:
            self.handle_exception(e)
            return None

    def format_datetime(self, formatted_datetime: datetime.datetime):
        try:
            if formatted_datetime is None:
                return None
            return formatted_datetime.strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            self.handle_exception(e)
            return None

    def check_res(self, res: datetime.date):
        """
        检查更新日期
        """
        try:
            return time.mktime(res.timetuple()) > (
                time.time() - self.config_setting.res
            )
        except Exception as e:
            self.handle_exception(e)
            return True

    def parse_update_date(self, update_text):
        try:
            date_format = "%Y-%m-%d"
            return datetime.datetime.strptime(update_text, date_format).date()
        except Exception as e:
            self.handle_exception(e, update_text)
            return None

    def check_update_date(self, update_date: datetime.date):
        """
        检查更新日期
        """
        try:
            return time.mktime(update_date.timetuple()) > (
                time.time() - self.config_setting.update
            )
        except Exception as e:
            self.handle_exception(e)
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
            return all(
                item not in city_text for item in self.config_setting.city_block_list
            )
        except Exception:
            return True

    def check_boss_title(self, boss_title_text: str):
        """
        检查人事
        """
        boss_title_text = boss_title_text.lower()
        return all(
            item not in boss_title_text
            for item in self.config_setting.boss_title_block_list
        )

    def check_offline(self, description_text, city_text):
        """
        检查面试方式
        """
        if self.config_setting.offline_interview:
            if any(
                item in description_text for item in self.config_setting.offline_list
            ):
                return any(
                    item in city_text for item in self.config_setting.offline_city_list
                )
        return True

    def check_industry(self, industry_text):
        """
        检查行业
        """
        return all(
            item not in industry_text
            for item in self.config_setting.industry_block_list
        )

    def check_name(self, name_text: str):
        """
        检查标题
        """
        name_text = name_text.lower()
        return all(
            item not in name_text for item in self.config_setting.name_block_list
        )

    def check_guide(self, guide_text: str):
        """
        检查导航
        """
        guide_text = guide_text.lower()
        return all(
            item not in guide_text for item in self.config_setting.guide_block_list
        )

    def check_company(self, company_text):
        """
        检查公司名称
        """
        return all(
            item not in company_text for item in self.config_setting.company_block_list
        )

    def save_state(self, wheels):
        with open(
            "state.json",
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(wheels, f, ensure_ascii=False)
        print(f"保存state.json成功：{wheels}")

    def load_state(self):
        try:
            env_state = os.getenv("STATE")
            if env_state:
                print(f"从环境变量获取state.json成功：{env_state}")
                with open(
                    "state.json",
                    "w",
                    encoding="utf-8",
                ) as f:
                    f.write(env_state)
                return json.loads(env_state)
            with open(
                "state.json",
                "r",
                encoding="utf-8",
            ) as f:
                return json.load(f)
        except Exception as e:
            self.handle_exception(e)
            return [[], [], [], 0]

    def handle_exception(self, exception, exc_value=""):
        traceback.print_exc()
        tb_str = traceback.format_exc()
        self.append_to_file("log.txt", f"异常信息：{tb_str}，{exception}，{exc_value}")
