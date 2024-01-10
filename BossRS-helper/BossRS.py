import datetime
import json
import pickle
import sys
import time
import re
import traceback
from urllib.parse import urlparse, parse_qs
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
import sqlite3
import undetected_chromedriver as uc
from chat import Chat
from rsinfo import RsInfo
import config

config_setting = config.load_config()

URL1 = "https://www.zhipin.com/web/geek/job?query="
URL2 = config_setting.query_params + "&salary="
URL3 = "&page="
URL4 = "https://www.zhipin.com/wapi/zpgeek/job/card.json?securityId="
URL5 = "&lid="
URL6 = "&sessionId="
URL7 = "&city="

driver = uc.Chrome(
    headless=config_setting.headless,
)
if len(config_setting.user_data_dir) > 0 and not config_setting.user_data_dir.isspace():
    driver.user_data_dir = config_setting.user_data_dir
WAIT = WebDriverWait(driver, config_setting.timeout)

conn = sqlite3.connect(config_setting.db_path)
cursor = conn.cursor()


def resume_submission(url):
    """
    投递简历
    """
    driver.get(url)
    check_dialog()
    check_verify(url)
    try:
        WAIT.until(
            ec.presence_of_element_located(
                (By.CSS_SELECTOR, "[class*='job-title clearfix']")
            )
        )
    except Exception:
        traceback.print_exc()
        return 1
    submissions = []
    urls = []
    job_elements = driver.find_elements(
        By.CSS_SELECTOR, "[class*='job-card-body clearfix']"
    )
    for job_element in job_elements:
        rsinfo = RsInfo()
        if is_ready_to_communicate(
            job_element.find_element(
                By.CSS_SELECTOR, "[class*='job-info clearfix']"
            ).get_attribute("innerHTML")
        ):
            rsinfo.communicate = "立即沟通"
        else:
            rsinfo.communicate = "继续沟通"
        url = job_element.find_element(By.CLASS_NAME, "job-card-left").get_attribute(
            "href"
        )
        id = get_encryptJobId(url)
        row = get_rsinfo(id)
        if row.id == id:
            # time.sleep(1)
            # continue
            rsinfo = row
        rsinfo.url = url.split("&securityId")[0]
        rsinfo.name = job_element.find_element(By.CLASS_NAME, "job-name").text
        rsinfo.city = job_element.find_element(By.CLASS_NAME, "job-area").text
        rsinfo.company = (
            job_element.find_element(By.CLASS_NAME, "company-name")
            .find_element(By.TAG_NAME, "a")
            .text
        )
        rsinfo.industry = (
            job_element.find_element(By.CLASS_NAME, "company-tag-list")
            .find_element(By.TAG_NAME, "li")
            .text
        )
        rsinfo.datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        rsinfo.id = id
        update_rsinfos(rsinfo)
        if (
            is_ready_to_communicate(rsinfo.communicate)
            and check_name(rsinfo.name)
            and check_city(rsinfo.city)
            and check_company(rsinfo.company)
            and check_industry(rsinfo.industry)
        ):
            urls.append(url)
    conn.commit()
    for url in urls:
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        lid = query_params.get("lid", [None])[0]
        security_id = query_params.get("securityId", [None])[0]
        try:
            driver.get(URL4 + security_id + URL5 + lid + URL6)
        except Exception:
            traceback.print_exc()
            continue
        time.sleep(1)
        WAIT.until(ec.presence_of_element_located((By.TAG_NAME, "pre")))
        page_source = driver.find_element(By.TAG_NAME, "pre").text
        data = json.loads(page_source)
        if data["message"] == "Success":
            rsinfo = get_rsinfo(get_encryptJobId(url))
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
            update_rsinfos(rsinfo)
            if not (
                check_description(rsinfo.description)
                and check_active(rsinfo.active)
                and check_city(rsinfo.address)
                and check_salary(rsinfo.salary)
                and check_experience(rsinfo.experience)
                and check_degree(rsinfo.degree)
                and check_bossTitle(rsinfo.boss_title)
            ):
                continue
        submissions.append(url)
    conn.commit()
    for submission in submissions:
        driver.get(submission)
        WAIT.until(
            ec.presence_of_element_located(
                (By.CSS_SELECTOR, "[class*='btn btn-startchat']")
            )
        )
        check_dialog()
        check_verify(submission)
        startchat = driver.find_element(By.CSS_SELECTOR, "[class*='btn btn-startchat']")
        try:
            rsinfo = get_rsinfo(get_encryptJobId(submission))
            rsinfo.guide = driver.find_element(
                By.CSS_SELECTOR, "[class*='pos-bread city-job-guide']"
            ).text
            if len(rsinfo.guide) > 2:
                rsinfo.guide = rsinfo.guide[2:]
            rsinfo.scale = driver.find_element(
                By.CSS_SELECTOR, ".sider-company > p:nth-child(4)"
            ).text
            if "人" not in rsinfo.scale:
                rsinfo.scale = ""
            rsinfo.update_date = driver.find_element(By.CSS_SELECTOR, "p.gray").text
            if len(rsinfo.update_date) > 4:
                rsinfo.update_date = rsinfo.update_date[4:]
            rsinfo.description = driver.find_element(
                By.CLASS_NAME, "job-detail-section"
            ).text
            try:
                rsinfo.fund = driver.find_element(
                    By.CSS_SELECTOR, "[class*='company-fund']"
                ).text
                if len(rsinfo.fund.splitlines()) > 1:
                    rsinfo.fund = rsinfo.fund.splitlines()[-1]
                rsinfo.res = driver.find_element(By.CSS_SELECTOR, ".res-time").text
                if len(rsinfo.res.splitlines()) > 1:
                    rsinfo.res = rsinfo.res.splitlines()[-1]
            except Exception:
                print(submission)
                traceback.print_exc()
                pass
            rsinfo.communicate = startchat.text
            update_rsinfos(rsinfo)
            if not (
                check_guide(rsinfo.guide)
                and check_scale(rsinfo.scale)
                and check_res(rsinfo.res)
                and check_update(rsinfo.update_date)
                and check_description(rsinfo.description)
                and check_offline(rsinfo.description, rsinfo.city)
                and check_fund(rsinfo.fund)
                and is_ready_to_communicate(rsinfo.communicate)
            ):
                continue
            if config_setting.chat:
                if not Chat.check(rsinfo.description):
                    continue
        except Exception:
            print(submission)
            traceback.print_exc()
            continue
        startchat.click()
        rsinfo = get_rsinfo(get_encryptJobId(submission))
        rsinfo.communicate = "继续沟通"
        update_rsinfos(rsinfo)
        if config_setting.chat_letter:
            try:
                time.sleep(3)
                Chat.send_letter_to_chat_box(
                    driver, Chat.generate_letter(rsinfo.description)
                )
                continue
            except Exception:
                print(submission)
                traceback.print_exc()
        try:
            WAIT.until(ec.presence_of_element_located((By.CLASS_NAME, "dialog-con")))
        except Exception:
            print(submission)
            traceback.print_exc()
            continue
        dialog_text = driver.find_element(By.CLASS_NAME, "dialog-con").text
        if "已达上限" in dialog_text:
            return -1
        check_dialog()
        time.sleep(1)
    conn.commit()
    return 0


def update_rsinfos(rsinfo):
    if len(rsinfo.id) == 0 or rsinfo.id.isspace():
        print("无法更新无效的对象")
        return
    cursor.execute("SELECT * FROM rsinfo WHERE id = ?", (rsinfo.id,))
    row = cursor.fetchone()
    if row:
        cursor.execute(
            "UPDATE rsinfo SET url=?, name=?, city=?, address=?, guide=?, scale=?, update_date=?, salary=?, experience=?, degree=?, company=?, industry=?, fund=?, res=?, boss=?, boss_title=?, active=?, description=?, communicate=?, datetime=? WHERE id=?",
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
            "INSERT INTO rsinfo (url, id, name, city, address, guide, scale, update_date, salary, experience, degree, company, industry, fund, res, boss, boss_title, active, description, communicate, datetime) VALUES     (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
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


def get_rsinfo(id):
    cursor.execute("SELECT * FROM rsinfo WHERE id = ?", (id,))
    row = cursor.fetchone()
    if row:
        return RsInfo(*row)
    else:
        return RsInfo()


def get_encryptJobId(url):
    match = re.search(r"/+([^/]+)\.html", url)
    if match:
        return match.group(1)
    else:
        return ""


def check_active(active_text):
    """
    检查活跃时间
    """
    return all(item not in active_text for item in config_setting.active_blacks)


def check_scale(scale_text):
    """
    检查规模
    """
    return all(item not in scale_text for item in config_setting.scale_blacks)


def check_experience(experience_text):
    """
    检查经验
    """
    return all(item not in experience_text for item in config_setting.experience_blacks)


def check_degree(degree_text):
    """
    检查学位
    """
    return all(item not in degree_text for item in config_setting.degree_blacks)


def check_fund(fund_text):
    """
    检查资金
    """
    if "-" in fund_text:
        return False
    if "万" in fund_text:
        fund_text = fund_text[:-3]
        numbers = re.findall("\d+\.\d+|\d+", fund_text)
        numbers = list(map(float, numbers))
        return numbers[0] > config_setting.fund_min
    return True


def check_salary(salary_text):
    """
    检查薪资
    """
    pattern = r"(\d+)-(\d+)K"
    match = re.search(pattern, salary_text)
    if match:
        low_salary = int(match.group(1))
        return low_salary < config_setting.salary_max


def check_description(description_text):
    """
    检查职位描述
    """
    if len(description_text) < config_setting.description_min:
        return False
    description_text = description_text.lower()
    if all(
        item not in description_text for item in config_setting.description_keywords
    ):
        return False
    if any(item in description_text for item in config_setting.description_blacks):
        return False
    if "截止日期" in description_text:
        exp_date_text = description_text[
            description_text.index("截止日期") + 5 : description_text.index("截止日期")
            + 15
        ]
        date_format = "%Y.%m.%d"
        try:
            if time.mktime(time.strptime(exp_date_text, date_format)) < time.time():
                return False
        except Exception:
            traceback.print_exc()
            pass
        description_text = (
            description_text[: description_text.index("截止日期")]
            + description_text[description_text.index("截止日期") + 15 :]
        )
    if "毕业时间" in description_text:
        graduation_time = description_text[
            description_text.index("毕业时间") : description_text.index("毕业时间") + 15
        ]
        graduation_time_min_blacks = ["24年-"]
        graduation_time_blacks = ["2020", "21", "22"]
        graduation_times = ["不限", "23"]
        graduation_times_max = ["-24", "-25"]
        if any(item in graduation_time for item in graduation_times):
            return True
        if any(item in graduation_time for item in graduation_time_min_blacks):
            return False
        if any(item in graduation_time for item in graduation_times_max):
            return True
        if any(item in graduation_time for item in graduation_time_blacks):
            return False
    graduations_experiences = ["23届", "23年", "24年及之前", "往届", "0-", "0～", "0~"]
    if any(item in description_text for item in graduations_experiences):
        return True
    graduations_max = ["24届", "24年", "24应届"]
    if any(item in description_text for item in graduations_max):
        return "23" in description_text
    graduations = ["应届" "毕业生" "实习生" "无经验"]
    if any(item in description_text for item in graduations):
        return True
    return all(
        item not in description_text
        for item in config_setting.description_experience_blacks
    )


def check_dialog():
    try:
        time.sleep(1)
        dialog_elements = driver.find_elements(By.CLASS_NAME, "dialog-container")
        if dialog_elements:
            if (
                "安全问题" in dialog_elements[-1].text
                or "沟通" in dialog_elements[-1].text
            ):
                close_elements = dialog_elements[-1].find_elements(
                    By.CLASS_NAME, "close"
                )
                if close_elements:
                    close_elements[-1].click()
                    time.sleep(1)
    except Exception:
        traceback.print_exc()


def check_verify(url):
    try:
        time.sleep(1)
        current_url = driver.current_url
        if "safe/verify-slider" in current_url:
            WebDriverWait(driver, 999).until(ec.url_changes(current_url))
            time.sleep(3)
            driver.get(url)
            time.sleep(6)
        time.sleep(1)
    except Exception:
        traceback.print_exc()


def check_res(res_text):
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
        traceback.print_exc()
        return True


def check_update(update_text):
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


def is_ready_to_communicate(startchat_text):
    """
    检查能否沟通
    """
    return "立即" in startchat_text


def check_city(city_text):
    """
    检查城市
    """
    try:
        return all(item not in city_text for item in config_setting.city_blacks)
    except Exception:
        return True


def check_bossTitle(bossTitle_text):
    """
    检查人事
    """
    bossTitle_text = bossTitle_text.lower()
    return all(item not in bossTitle_text for item in config_setting.bossTitle_blacks)


def check_offline(description_text, city_text):
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
            return any(item in city_text for item in config_setting.offline_citys)
    return True


def check_industry(industry_text):
    """
    检查行业
    """
    return all(item not in industry_text for item in config_setting.industry_blacks)


def check_name(name_text):
    """
    检查标题
    """
    name_text = name_text.lower()
    return all(item not in name_text for item in config_setting.name_blacks)


def check_guide(guide_text):
    """
    检查导航
    """
    guide_text = guide_text.lower()
    return all(item not in guide_text for item in config_setting.guide_blacks)


def check_company(company_text):
    """
    检查公司名称
    """
    return all(item not in company_text for item in config_setting.company_blacks)


driver.get("https://www.zhipin.com")
time.sleep(5)
with open(config_setting.cookie_path, "rb") as f:
    cookies = pickle.load(f)
for cookie in cookies:
    driver.add_cookie(cookie)
time.sleep(2)
driver.get("https://www.zhipin.com")
time.sleep(2)

for city in config_setting.query_citys:
    for query in config_setting.querys:
        for salary in config_setting.salarys:
            for i in range(config_setting.range_min, config_setting.range_max):
                if (
                    resume_submission(
                        URL1 + query + URL7 + city + URL2 + salary + URL3 + str(i)
                    )
                    == -1
                ):
                    sys.exit()
driver.quit()
conn.close()
