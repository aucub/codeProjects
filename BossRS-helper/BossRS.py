import codecs
import json
import pickle
import sys
import time
import re
import traceback
from urllib.parse import urlparse, parse_qs
from attr import asdict
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
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

driver = uc.Chrome(
    headless=config_setting.headless,
)
if len(config_setting.user_data_dir) > 0 and not config_setting.user_data_dir.isspace():
    driver.user_data_dir = config_setting.user_data_dir
WAIT = WebDriverWait(driver, config_setting.timeout)

rsinfo_dict = dict()


def resume_submission(url):
    """
    投递简历
    """
    driver.get(url)
    time.sleep(3)
    check_dialog()
    check_verify(url)
    try:
        WAIT.until(
            ec.presence_of_element_located(
                (By.CSS_SELECTOR, "[class*='job-title clearfix']")
            )
        )
    except:
        traceback.print_exc()
        return 1
    submissions = []
    urls = []
    job_elements = driver.find_elements(
        By.CSS_SELECTOR, "[class*='job-card-body clearfix']"
    )
    for job_element in job_elements:
        rsinfo = RsInfo()
        rsinfo.name = job_element.find_element(By.CLASS_NAME, "job-name").text
        rsinfo.city = job_element.find_element(By.CLASS_NAME, "job-area").text
        rsinfo.company = (
            job_element.find_element(By.CLASS_NAME, "company-name")
            .find_element(By.TAG_NAME, "a")
            .text
        )
        rsinfo.companyTag = (
            job_element.find_element(By.CLASS_NAME, "company-tag-list")
            .find_element(By.TAG_NAME, "li")
            .text
        )
        rsinfo.communicate = job_element.find_element(
            By.CSS_SELECTOR, "[class*='job-info clearfix']"
        ).get_attribute("innerHTML")
        rsinfo.url = job_element.find_element(
            By.CLASS_NAME, "job-card-left"
        ).get_attribute("href")
        rsinfo.id = get_encryptJobId(rsinfo.url)
        if rsinfo.id in rsinfo_dict:
            if not is_ready_to_communicate(rsinfo_dict[rsinfo.id].communicate):
                continue
        if (
            check_name(rsinfo.name)
            and check_city(rsinfo.city)
            and check_company(rsinfo.company)
            and check_industry(rsinfo.companyTag)
            and is_ready_to_communicate(rsinfo.communicate)
        ):
            urls.append(rsinfo.url)
        rsinfo_dict[rsinfo.id] = rsinfo
    for url in urls:
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        lid = query_params.get("lid", [None])[0]
        security_id = query_params.get("securityId", [None])[0]
        try:
            driver.get(URL4 + security_id + URL5 + lid + URL6)
        except:
            traceback.print_exc()
            continue
        time.sleep(2)
        WAIT.until(ec.presence_of_element_located((By.TAG_NAME, "pre")))
        page_source = driver.find_element(By.TAG_NAME, "pre").text
        data = json.loads(page_source)
        if data["message"] == "Success":
            rsinfo = rsinfo_dict[get_encryptJobId(url)]
            rsinfo.description = data["zpData"]["jobCard"]["postDescription"]
            rsinfo.active = data["zpData"]["jobCard"]["activeTimeDesc"]
            rsinfo.address = data["zpData"]["jobCard"]["address"]
            rsinfo.id = data["zpData"]["jobCard"]["encryptJobId"]
            rsinfo.salary = data["zpData"]["jobCard"]["salaryDesc"]
            rsinfo.experience = data["zpData"]["jobCard"]["experienceName"]
            rsinfo.degree = data["zpData"]["jobCard"]["degreeName"]
            rsinfo.boss = data["zpData"]["jobCard"]["bossName"]
            rsinfo.bossTitle = data["zpData"]["jobCard"]["bossTitle"]
            rsinfo_dict[get_encryptJobId(url)] = rsinfo
            if not (
                check_description(rsinfo.description)
                and check_active(rsinfo.active)
                and check_city(rsinfo.address)
                and check_salary(rsinfo.salary)
                and check_experience(rsinfo.experience)
                and check_degree(rsinfo.degree)
                and check_bossTitle(rsinfo.bossTitle)
            ):
                continue
        submissions.append(url)
    save_rsinfos()
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
            rsinfo = rsinfo_dict[get_encryptJobId(submission)]
            rsinfo.guide = driver.find_element(
                By.CSS_SELECTOR, "[class*='pos-bread city-job-guide']"
            ).text
            rsinfo.scale = driver.find_element(
                By.CSS_SELECTOR, ".sider-company > p:nth-child(4)"
            ).text
            rsinfo.update = driver.find_element(By.CSS_SELECTOR, "p.gray").text
            rsinfo.description = driver.find_element(
                By.CLASS_NAME, "job-detail-section"
            ).text
            rsinfo.fund = driver.find_element(
                By.CSS_SELECTOR, "[class*='company-fund']"
            ).text
            rsinfo.res = driver.find_element(By.CSS_SELECTOR, ".res-time").text
            rsinfo.communicate = startchat.text
            rsinfo_dict[get_encryptJobId(submission)] = rsinfo
            if not (
                check_guide(rsinfo.guide)
                and check_scale(rsinfo.scale)
                and check_res(rsinfo.res)
                and check_update(rsinfo.update)
                and check_description(rsinfo.description)
                and check_offline(rsinfo.description, rsinfo.city)
                and check_fund(rsinfo.fund)
                and is_ready_to_communicate(rsinfo.communicate)
            ):
                continue
            if config_setting.chat:
                if not Chat.check(rsinfo.description):
                    continue
        except:
            traceback.print_exc()
            continue
        startchat.click()
        rsinfo = rsinfo_dict[get_encryptJobId(submission)]
        rsinfo.communicate = "继续沟通"
        rsinfo_dict[get_encryptJobId(submission)] = rsinfo
        try:
            WAIT.until(ec.presence_of_element_located((By.CLASS_NAME, "dialog-con")))
        except:
            traceback.print_exc()
            continue
        dialog_text = driver.find_element(By.CLASS_NAME, "dialog-con").text
        if "已达上限" in dialog_text:
            return -1
        check_dialog()
        time.sleep(3)
    save_rsinfos()
    return 0


def save_rsinfos():
    rsinfo_list = []
    for rsinfo in rsinfo_dict.values():
        rsinfo_list.append(json.dumps(asdict(rsinfo), ensure_ascii=False))
    with open("rsinfo.txt", "w", encoding="utf-8") as f:
        for item in rsinfo_list:
            f.write(item + "\n")


def load_rsinfos():
    rsinfo_dict = {}
    with codecs.open("rsinfo.txt", "r", "utf-8-sig") as f:
        for line in f:
            json_dict = json.loads(line)
            rsinfo = RsInfo(**json_dict)
            rsinfo_dict[rsinfo.id] = rsinfo


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
    lines = fund_text.splitlines()
    fund_text = lines[-1]
    fund_text = fund_text[:-3]
    return all(fund_text not in item for item in config_setting.fund_blacks)


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
            description_text.index("截止日期") + 5 : description_text.index("截止日期") + 15
        ]
        date_format = "%Y.%m.%d"
        try:
            if time.mktime(time.strptime(exp_date_text, date_format)) < time.time():
                return False
        except:
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
    graduations_experiences = ["23届", "23年", "24年及之前", "往届", "0-"]
    if any(item in description_text for item in graduations_experiences):
        return True
    graduations_max = ["24届", "24年", "24应届"]
    if any(item in description_text for item in graduations_max):
        return "23" in description_text
    graduations = ["应届" "无经验"]
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
            driver.find_element(By.CLASS_NAME, "icon-close").click
        time.sleep(1)
    except:
        traceback.print_exc()


def check_verify(url):
    try:
        time.sleep(1)
        current_url = driver.current_url
        if "safe/verify-slider" in current_url:
            WebDriverWait(driver, 00).until(ec.url_changes(current_url))
            time.sleep(3)
            driver.get(url)
            time.sleep(6)
        time.sleep(1)
    except:
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
    except:
        traceback.print_exc()
        return True


def check_update(update_text):
    """
    检查更新日期
    """
    update_text = update_text[-10:]
    date_format = "%Y-%m-%d"
    return time.mktime(time.strptime(update_text, date_format)) > (
        time.time() - config_setting.update
    )


def is_ready_to_communicate(startchat_text):
    """
    检查能否沟通
    """
    return "立即" in startchat_text


def check_city(city_text):
    """
    检查城市
    """
    return all(item not in city_text for item in config_setting.city_blacks)


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
# 加载之前保存的cookie
with open("cookies.pkl", "rb") as f:
    cookies = pickle.load(f)
# # 将cookie添加到浏览器中
for cookie in cookies:
    driver.add_cookie(cookie)
time.sleep(5)
driver.get("https://www.zhipin.com")

load_rsinfos()

time.sleep(5)

for item in config_setting.querys:
    for salary in config_setting.salarys:
        for i in range(config_setting.range_min, config_setting.range_max):
            if resume_submission(URL1 + item + URL2 + salary + URL3 + str(i)) == -1:
                sys.exit()
driver.quit()
