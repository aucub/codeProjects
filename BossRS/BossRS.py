import json
import os
import time
import undetected_chromedriver as uc
from urllib.parse import urlparse, parse_qs
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

URL1 = "https://www.zhipin.com/web/geek/job?query="
URL2 = "&city=100010000&experience=102,101,103,104&scale=303,304,305,306,302&degree=209,208,206,202,203&salary="
URL3 = "&page="
resumes = set()
URL4 = "https://www.zhipin.com/wapi/zpgeek/job/card.json?securityId="
URL5 = "&lid="
URL6 = "&sessionId="

driver = uc.Chrome(headless=False, version_main=118)
WAIT = WebDriverWait(driver, 30)


def resume_submission(url):
    try:
        driver.get(url)
        time.sleep(15)
        WAIT.until(
            ec.presence_of_element_located(
                (By.CSS_SELECTOR, "[class*='job-title clearfix']")
            )
        )
        jobs = []
        urls = []
        job_elements = driver.find_elements(
            By.CSS_SELECTOR, "[class*='job-card-body clearfix']"
        )
        for jobElement in job_elements:
            try:
                if (
                    check_title(jobElement.find_element(By.CLASS_NAME, "job-name").text)
                    and check_city(
                        jobElement.find_element(By.CLASS_NAME, "job-area").text
                    )
                    and check_company(
                        jobElement.find_element(By.CLASS_NAME, "company-name")
                        .find_element(By.TAG_NAME, "a")
                        .text
                    )
                    and check_industry(
                        jobElement.find_element(By.CLASS_NAME, "company-tag-list")
                        .find_element(By.TAG_NAME, "li")
                        .text
                    )
                    and is_ready_to_communicate(
                        jobElement.find_element(
                            By.CSS_SELECTOR, "[class*='job-info clearfix']"
                        ).get_attribute("innerHTML")
                    )
                ):
                    urls.append(
                        jobElement.find_element(
                            By.CLASS_NAME, "job-card-left"
                        ).get_attribute("href")
                    )
            except:
                pass
        for url in urls:
            resume = url.split("/")[-1].split(".")[0]
            if resume not in resumes:
                resumes.add(resume)
                try:
                    parsed_url = urlparse(url)
                    query_params = parse_qs(parsed_url.query)
                    lid = query_params.get("lid", [None])[0]
                    security_id = query_params.get("securityId", [None])[0]
                    driver.get(URL4 + security_id + URL5 + lid + URL6)
                    time.sleep(3)
                    page_source = driver.find_element(By.TAG_NAME, "pre").text
                    data = json.loads(page_source)
                    if data["message"] == "Success":
                        description = data["zpData"]["jobCard"]["postDescription"]
                        active = data["zpData"]["jobCard"]["activeTimeDesc"]
                        if not (check_sec(description) and check_active_time(active)):
                            continue
                except:
                    pass
                jobs.append(url)
        for job in jobs:
            try:
                driver.get(job)
                WAIT.until(
                    ec.presence_of_element_located(
                        (By.CSS_SELECTOR, "[class*='btn btn-startchat']")
                    )
                )
                btn = driver.find_element(
                    By.CSS_SELECTOR, "[class*='btn btn-startchat']"
                )
                if not (
                    check_active_time(
                        driver.find_element(By.CLASS_NAME, "boss-active-time").text
                    )
                    and check_res()
                    and check_sec(
                        driver.find_element(By.CLASS_NAME, "job-detail-section").text
                    )
                    and is_ready_to_communicate(btn.text)
                ):
                    continue
                btn.click()
                WAIT.until(
                    ec.presence_of_element_located((By.CLASS_NAME, "dialog-con"))
                )
                dialog_text = driver.find_element(By.CLASS_NAME, "dialog-con").text
                if "已达上限" in dialog_text:
                    return -1
                time.sleep(3)
            except:
                pass
        with open("resume.txt", "w") as file:
            file.write("\n".join(resumes))
        return 0
    except:
        return 0


def check_active_time(active_time_text):
    try:
        active_time_blacks = ["半年", "月内", "周内", "7日", "本月", "本周"]
        return not any(item in active_time_text for item in active_time_blacks)
    except:
        return True


def check_city(city_text):
    try:
        city_blacks = ["沈阳", "乌鲁木齐", "乌兰察布", "大连", "哈尔滨", "呼和浩特"]
        return not any(item in city_text for item in city_blacks)
    except:
        return True


def check_industry(industry_text):
    try:
        industry_blacks = ["培训", "院校", "房产", "经纪", "工程施工", "中介"]
        return not any(item in industry_text for item in industry_blacks)
    except:
        return True


def check_sec(sec_text):
    try:
        sec_text = sec_text.lower()
        sec_keywords = [
            "java",
            "python",
            "spring",
            "sql",
            "linux",
            "j2ee",
            "web",
            "bug",
            "数据库",
            "后端",
            "软件测试",
            "开发",
            "计算机",
            "编程",
        ]
        if not any(item in sec_text for item in sec_keywords):
            return False
        sec_blacks = [
            "不接受应届",
            "应届生勿",
            "日语",
            "精通c#",
            "node开发经验",
            "用户界面编程",
            "mcu",
            "dsp",
            "ecu",
            "uds",
            "cdd",
            "diva",
            "硬件测试",
            "汽车",
            "车厂",
            "机器人",
            "硬件控制",
            "串口",
            "布线",
            "上位",
            "销售",
            "营销",
            "车间",
            "车型",
            "家具",
            "售前",
            "电路",
            "电气",
            "弱电",
            "变频",
            "plc",
            "pms",
            "配电",
            "电力",
            "家电",
            "电能",
            "采购",
            "美妆",
            "污染",
            "大气",
            "危废",
            "气动",
            "液压",
            "电控",
            "给排水",
            "水利",
            "水务",
            "水文",
            "水资源",
            "化工",
            "石油",
            "土建",
            "手机厂商",
            "请勿联系",
        ]
        if any(item in sec_text for item in sec_blacks):
            return False
        if "毕业时间" in sec_text:
            graduation_time_blacks = ["2020", "2021", "2022"]
            graduation_time = sec_text[
                sec_text.index("毕业时间") : sec_text.index("毕业时间") + 15
            ]
            if any(item in graduation_time for item in graduation_time_blacks):
                return False
        if "截止日期" in sec_text:
            try:
                exp_date_text = sec_text[
                    sec_text.index("截止日期") + 5 : sec_text.index("截止日期") + 15
                ]
                date_format = "%Y.%m.%d"
                if time.mktime(time.strptime(exp_date_text, date_format)) < time.time():
                    return False
            except:
                pass
        secs = ["23届", "23年", "往届", "0-1年", "0-2年", "0-3年"]
        if any(item in sec_text for item in secs):
            return True
        if "24届" in sec_text and sec_text.index("24届") >= 5:
            return "23" in sec_text[sec_text.index("24届") - 5 : sec_text.index("24届")]
        if "24年" in sec_text and sec_text.index("24年") >= 5:
            return "23" in sec_text[sec_text.index("24年") - 5 : sec_text.index("24年")]
        secs1 = ["应届", "毕业"]
        if any(item in sec_text for item in secs1):
            return True
        sec_blacks1 = [
            "年以上",
            "年及以上",
            "年或以上",
            "1-2年",
            "1-3年",
            "1年-3年",
            "2-3年",
            "3-5年",
            "年(含)以上",
        ]
        return not any(item in sec_text for item in sec_blacks1)
    except:
        return True


def check_title(title_text):
    try:
        title_text = title_text.lower()
        title_blacks = [
            "助教",
            "销售",
            "日",
            "员",
            "产品开发",
            "嵌入式开发",
            "单片机",
            "游戏",
            "电话",
            "选址",
            "外贸",
            "网络优化",
            "客服",
            "实验",
            "弱电",
            "电气",
            "ic",
            "硬件",
            "教师",
            "讲师",
            "老师",
            "推广",
            "培训",
            "训练",
            "残",
            "高级",
            "创业",
            "合伙",
            "光学",
            "顾问",
            "仿真",
            "cam",
            "座舱",
            "主管",
            "经理",
            "基金",
            "三维",
            "芯片",
            "布料",
            ".net",
            "市场",
            "c++",
            "高性能",
            "环保",
            "内部",
            "财务",
            "采购",
            "人士",
            "管家",
            "架构师",
            "水务",
            "英语",
            "渗透",
            "01",
            "资深",
            "兼职",
            "台湾",
        ]
        return not any(item in title_text for item in title_blacks)
    except:
        return True


def check_company(company_text):
    try:
        company_blacks = ["培训", "学校", "教育"]
        return not any(item in company_text for item in company_blacks)
    except:
        return True


def check_res():
    try:
        res_element = driver.find_element(By.CSS_SELECTOR, ".res-time")
        res_text = res_element.text[-10:]
        date_format = "%Y-%m-%d"
        return time.mktime(time.strptime(res_text, date_format)) < (
            time.time() - 31536000
        )
    except:
        return True


def is_ready_to_communicate(btn_text):
    return "立即" in btn_text


if not os.path.exists("resume.txt"):
    open("resume.txt", "w").close()
with open("resume.txt", "r") as file:
    for line in file:
        string = line.strip()
        if string not in resumes:
            resumes.add(string)
driver.get("https://www.zhipin.com/web/user/?ka=header-login")
WAIT.until(
    ec.presence_of_element_located(
        (By.CSS_SELECTOR, "[class*='btn-sign-switch ewm-switch']")
    )
)
driver.find_element(By.CSS_SELECTOR, "[class*='btn-sign-switch ewm-switch']").click()
time.sleep(20)
Query = [
    "Java",
    "Java测试开发",
    "Java软件测试",
    "软件测试开发",
    "软件测试",
    "Java软件实施",
    "软件自动化测试",
    "软件功能测试",
    "软件实施",
    # "Java运维开发",
    # "Python软件测试",
    # "后端开发",
    # "软件开发",
    # "全栈工程师",
    # "软件需求分析",
    # "软件性能测试",
    # "Python",
    # "Node.js",
    # "数据分析",
    # "数据挖掘",
    # "DBA",
    # "Hadoop",
    # "JavaScript",
    # "软件技术文档",
]
for item in Query:
    for i in range(1, 10):
        try:
            if resume_submission(URL1 + item + URL2 + "404" + URL3 + str(i)) == -1:
                exit()
        except:
            continue
    for i in range(1, 10):
        try:
            if resume_submission(URL1 + item + URL2 + "403" + URL3 + str(i)) == -1:
                exit()
        except:
            continue
driver.quit()
