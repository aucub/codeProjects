import datetime
import os
import pickle
import sys
import time
import re
import traceback
from urllib.parse import urlparse, parse_qs
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
import sqlite3
import undetected_chromedriver as uc
from chat import Chat
from dotenv import load_dotenv
from rsinfo import RsInfo
import config

config_setting = config.load_config()

URL1 = "https://www.zhipin.com/web/geek/job?query="
URL2 = config_setting.query_param + "&salary="
URL3 = "&page="
URL4 = "https://www.zhipin.com/wapi/zpgeek/job/card.json?securityId="
URL5 = "&lid="
URL6 = "&sessionId="
URL7 = "&city="

load_dotenv()
chrome_options = uc.ChromeOptions()
chrome_location = str(os.getenv("CHROME_LOCATION"))
if (
    len(config_setting.chrome_location) > 0
    and not config_setting.chrome_location.isspace()
) or (len(chrome_location) > 0 and not chrome_location.isspace()):
    chrome_options.binary_location = config_setting.chrome_location

driver = uc.Chrome(headless=config_setting.headless, options=chrome_options)

if len(config_setting.user_data_dir) > 0 and not config_setting.user_data_dir.isspace():
    driver.user_data_dir = config_setting.user_data_dir

WAIT = WebDriverWait(driver, config_setting.timeout)

conn = sqlite3.connect(config_setting.db_path)
cursor = conn.cursor()


def query_url(url):
    """
    搜索职位
    """
    driver.get(url)
    check_dialog()
    check_verify(url)
    try:
        find_element_list = WAIT.until(
            ec.any_of(
                ec.presence_of_all_elements_located(
                    (By.CLASS_NAME, "job-card-wrapper")
                ),
                ec.presence_of_element_located((By.CLASS_NAME, "job-empty-wrapper")),
            )
        )
    except TimeoutException:
        return 1
    except Exception:
        traceback.print_exc()
        return 1
    if not isinstance(find_element_list, list):
        return 0
    url_list = []
    for job_element in find_element_list:
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
            if config_setting.skip_known:
                time.sleep(config_setting.sleep)
                continue
            else:
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
        update_rsinfo(rsinfo)
        if check_rsinfo(rsinfo, "query"):
            url_list.append(url)
    conn.commit()
    url_list_process(url_list)


def url_list_process(url_list):
    url_list = check_url_list(url_list)
    conn.commit()
    detail(url_list)
    conn.commit()


def check_url_list(url_list):
    card_url_list = []
    for url in url_list:
        if check_card(url):
            card_url_list.append(url)
    return card_url_list


def detail(url_list):
    for url in url_list:
        try:
            driver.get(url)
            check_verify(url)
            WAIT.until(
                ec.presence_of_element_located(
                    (By.CSS_SELECTOR, "[class*='btn btn-startchat']")
                )
            )
            check_dialog()
            rsinfo = get_rsinfo(get_encryptJobId(url))
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
                print(url)
                traceback.print_exc()
                pass
            rsinfo.communicate = driver.find_element(
                By.CSS_SELECTOR, "[class*='btn btn-startchat']"
            ).text
            update_rsinfo(rsinfo)
            if not check_rsinfo(rsinfo, "detail"):
                continue
            if config_setting.chat:
                if not Chat.check(rsinfo.description):
                    continue
            startchat(url)
        except Exception:
            print(url)
            traceback.print_exc()
            continue


def startchat(url: str):
    description = driver.find_element(By.CLASS_NAME, "job-sec-text").text
    driver.find_element(By.CSS_SELECTOR, "[class*='btn btn-startchat']").click()
    rsinfo = get_rsinfo(get_encryptJobId(url))
    rsinfo.communicate = "继续沟通"
    update_rsinfo(rsinfo)
    rsinfo.description = description
    try:
        find_element = WAIT.until(
            ec.any_of(
                ec.presence_of_element_located((By.CLASS_NAME, "dialog-con")),
                ec.presence_of_element_located((By.CSS_SELECTOR, "#chat-input")),
            )
        )
    except Exception:
        print(url)
        traceback.print_exc()
        return
    if "chat" in driver.current_url:
        try:
            send_greet_to_chat_box(Chat.generate_greet(rsinfo))
        except Exception:
            print(url)
            traceback.print_exc()
        return
    if "已达上限" in find_element.text:
        sys.exit()
    check_dialog()
    time.sleep(config_setting.sleep)


def send_greet_to_chat_box(greet):
    chat_box = WAIT.until(
        ec.presence_of_element_located((By.CSS_SELECTOR, "#chat-input"))
    )
    chat_box.clear()
    chat_box.send_keys(greet)
    time.sleep(config_setting.sleep)
    driver.find_element(
        By.CSS_SELECTOR,
        "#container > div > div > div.chat-conversation > div.message-controls > div > div.chat-op > button",
    ).click()
    time.sleep(config_setting.sleep)


def check_card(url: str):
    query_params = parse_qs(urlparse(url).query)
    lid = query_params.get("lid", [None])[0]
    security_id = query_params.get("securityId", [None])[0]
    try:
        response = requests.get(
            URL4 + security_id + URL5 + lid + URL6,
            cookies=requests_cookies,
            headers=requests_headers,
        )
        if response.status_code == 200:
            data = response.json()
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
            update_rsinfo(rsinfo)
            return check_rsinfo(rsinfo, "card")
        else:
            print(url)
            print(response.text)
            detail(url)
    except Exception:
        print(url)
        traceback.print_exc()


def check_rsinfo(rsinfo: RsInfo, stage: str):
    if stage == "query":
        return (
            is_ready_to_communicate(rsinfo.communicate)
            and check_name(rsinfo.name)
            and check_city(rsinfo.city)
            and check_company(rsinfo.company)
            and check_industry(rsinfo.industry)
        )
    elif stage == "card":
        return (
            check_description(rsinfo.description)
            and check_active(rsinfo.active)
            and check_city(rsinfo.address)
            and check_salary(rsinfo.salary)
            and check_experience(rsinfo.experience)
            and check_degree(rsinfo.degree)
            and check_boss_title(rsinfo.boss_title)
        )
    elif stage == "detail":
        return (
            check_guide(rsinfo.guide)
            and check_scale(rsinfo.scale)
            and check_res(rsinfo.res)
            and check_update(rsinfo.update_date)
            and check_description(rsinfo.description)
            and check_offline(rsinfo.description, rsinfo.city)
            and check_fund(rsinfo.fund)
            and is_ready_to_communicate(rsinfo.communicate)
        )


def update_rsinfo(rsinfo):
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
    return all(item not in active_text for item in config_setting.active_block_list)


def check_scale(scale_text):
    """
    检查规模
    """
    return all(item not in scale_text for item in config_setting.scale_block_list)


def check_experience(experience_text):
    """
    检查经验
    """
    return all(
        item not in experience_text for item in config_setting.experience_block_list
    )


def check_degree(degree_text):
    """
    检查学位
    """
    return all(item not in degree_text for item in config_setting.degree_block_list)


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
        item not in description_text for item in config_setting.description_keyword_list
    ):
        return False
    if any(item in description_text for item in config_setting.description_block_list):
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
    if config_setting.graduate != 0:
        graduate = config_setting.graduate
        if "毕业时间" in description_text:
            graduation_time = description_text[
                description_text.index("毕业时间") : description_text.index("毕业时间")
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


def check_dialog():
    try:
        time.sleep(config_setting.sleep)
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
                    time.sleep(config_setting.sleep)
    except Exception:
        traceback.print_exc()


def check_verify(url):
    try:
        time.sleep(config_setting.sleep)
        current_url = driver.current_url
        if "safe/verify-slider" in current_url:
            WebDriverWait(driver, 999).until(ec.url_changes(current_url))
            time.sleep(config_setting.sleep)
            driver.get(url)
            time.sleep(config_setting.sleep)
        time.sleep(config_setting.sleep)
        if "403.html" in current_url or "error.html" in current_url:
            print(driver.find_element(By.CLASS_NAME, "text").text)
            sys.exit()
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
        return all(item not in city_text for item in config_setting.city_block_list)
    except Exception:
        return True


def check_boss_title(boss_title_text):
    """
    检查人事
    """
    boss_title_text = boss_title_text.lower()
    return all(
        item not in boss_title_text for item in config_setting.boss_title_block_list
    )


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
            return any(item in city_text for item in config_setting.offline_city_list)
    return True


def check_industry(industry_text):
    """
    检查行业
    """
    return all(item not in industry_text for item in config_setting.industry_block_list)


def check_name(name_text):
    """
    检查标题
    """
    name_text = name_text.lower()
    return all(item not in name_text for item in config_setting.name_block_list)


def check_guide(guide_text):
    """
    检查导航
    """
    guide_text = guide_text.lower()
    return all(item not in guide_text for item in config_setting.guide_block_list)


def check_company(company_text):
    """
    检查公司名称
    """
    return all(item not in company_text for item in config_setting.company_block_list)


def stealth():
    if config_setting.stealth:
        if not os.path.isfile(config_setting.stealth_path):
            response = requests.get(config_setting.stealth_url)
            if response.status_code == 200:
                with open(config_setting.stealth_path, "w") as f:
                    f.write(response.text)
        else:
            print(
                f"Failed to download {config_setting.stealth_url}. Status code: {response.status_code}"
            )
            return
        with open(config_setting.stealth_path, "r") as f:
            stealth_js = f.read()
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument", {"source": stealth_js}
        )


driver.get("https://www.zhipin.com")
stealth()
with open(config_setting.cookie_path, "rb") as f:
    cookies = pickle.load(f)
for cookie in cookies:
    driver.add_cookie(cookie)
driver.get("https://www.zhipin.com/web/geek/job?query=")
check_verify("https://www.zhipin.com/web/geek/job?query=")
time.sleep(config_setting.sleep)
requests_cookies = {}
cookies = driver.get_cookies()
for cookie in cookies:
    requests_cookies[cookie["name"]] = cookie["value"]
requests_headers = {
    "User-Agent": driver.execute_script("return navigator.userAgent"),
}

for city in config_setting.query_city_list:
    for query in config_setting.query_list:
        for salary in config_setting.salary_list:
            for page in range(config_setting.page_min, config_setting.page_max):
                query_url(URL1 + query + URL7 + city + URL2 + salary + URL3 + str(page))
driver.quit()
conn.close()
