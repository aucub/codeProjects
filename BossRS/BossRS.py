import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from urllib.parse import urlparse, parse_qs
import json

URL1 = "https://www.zhipin.com/web/geek/job?query="
URL2 = "&city=100010000&experience=102,101,103,104&degree=209,208,206,202,203&scale=303,304,305,306,302&salary="
URL3 = "&page="
resumesr = set()
URL4 = "https://www.zhipin.com/wapi/zpgeek/job/card.json?securityId="
URL5 = "&lid="
URL6 = "&sessionId="

driver = webdriver.Chrome()
WAIT = WebDriverWait(driver, 30)


def resumeSubmission(url):
    resumesw = set()
    try:
        driver.get(url)
        time.sleep(15)
        WAIT.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "[class*='job-title clearfix']")
            )
        )
        jobList = []
        urlList = []
        jobElements = driver.find_elements(
            By.CSS_SELECTOR, "[class*='job-card-body clearfix']"
        )
        for jobElement in jobElements:
            try:
                if (
                    checkTitle(jobElement.find_element(By.CLASS_NAME, "job-name").text)
                    and checkCity(
                        jobElement.find_element(By.CLASS_NAME, "job-area").text
                    )
                    and checkCompany(
                        jobElement.find_element(By.CLASS_NAME, "company-name")
                        .find_element(By.TAG_NAME, "a")
                        .text
                    )
                    and checkIndustry(
                        jobElement.find_element(By.CLASS_NAME, "company-tag-list")
                        .find_element(By.TAG_NAME, "li")
                        .text
                    )
                    and isReadyToCommunicate(
                        jobElement.find_element(
                            By.CSS_SELECTOR, "[class*='job-info clearfix']"
                        ).get_attribute("innerHTML")
                    )
                ):
                    urlList.append(
                        jobElement.find_element(
                            By.CLASS_NAME, "job-card-left"
                        ).get_attribute("href")
                    )
            except:
                pass
        for url in urlList:
            resume = url.split("/")[-1].split(".")[0]
            if resume not in resumesr:
                resumesw.add(resume)
                resumesr.add(resume)
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
                        if not (checkSec(description) and checkActiveTime(active)):
                            continue
                except:
                    pass
                jobList.append(url)
        for job in jobList:
            try:
                driver.get(job)
                WAIT.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "[class*='btn btn-startchat']")
                    )
                )
                btn = driver.find_element(
                    By.CSS_SELECTOR, "[class*='btn btn-startchat']"
                )
                if not (
                    checkActiveTime(
                        driver.find_element(By.CLASS_NAME, "boss-active-time").text
                    )
                    and checkRes()
                    and checkSec(
                        driver.find_element(By.CLASS_NAME, "job-detail-section").text
                    )
                    and isReadyToCommunicate(btn.text)
                ):
                    continue
                btn.click()
                WAIT.until(
                    EC.presence_of_element_located((By.CLASS_NAME, "dialog-con"))
                )
                dialogText = driver.find_element(By.CLASS_NAME, "dialog-con").text
                if "已达上限" in dialogText:
                    return -1
                time.sleep(3)
            except:
                pass
        with open("resume.txt", "a") as file:
            file.write("\n")
            file.write("\n".join(resumesw))
        return 0
    except:
        return 0


def checkActiveTime(activeTimeText):
    try:
        activeTimeBlackList = ["半年", "月内", "周内", "7日", "本月", "本周"]
        return not any(item in activeTimeText for item in activeTimeBlackList)
    except:
        return True


def checkCity(cityText):
    try:
        cityBlackList = ["沈阳", "乌鲁木齐", "乌兰察布", "大连", "哈尔滨", "呼和浩特"]
        return not any(item in cityText for item in cityBlackList)
    except:
        return True


def checkIndustry(industryText):
    try:
        industryBlackList = ["培训", "院校", "房产", "经纪", "中介"]
        return not any(item in industryText for item in industryBlackList)
    except:
        return True


def checkSec(secText):
    try:
        secText = secText.lower()
        KEYWORDS = [
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
        if not any(item in secText for item in KEYWORDS):
            return False
        secBlackList = [
            "不接受应届",
            "日语",
            "精通c#",
            "node开发经验",
            "用户界面编程",
            "mcu",
            "dsp",
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
            "家具",
            "售前",
            "电路",
            "电气",
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
        ]
        if any(item in secText for item in secBlackList):
            return False
        if "毕业时间" in secText:
            graduationTimeBlackList = ["2020", "2021", "2022"]
            graduationTime = secText[secText.index("毕业时间") : secText.index("毕业时间") + 15]
            if any(item in graduationTime for item in graduationTimeBlackList):
                return False
        if "截止日期" in secText:
            try:
                expDateText = secText[
                    secText.index("截止日期") + 5 : secText.index("截止日期") + 15
                ]
                dateFormat = "%Y.%m.%d"
                if time.mktime(time.strptime(expDateText, dateFormat)) < time.time():
                    return False
            except:
                pass
        secList = ["23届", "23年", "应届", "往届", "毕业", "0-1年", "0-2年", "0-3年"]
        if any(item in secText for item in secList):
            return True
        if "24届" in secText and secText.index("24届") >= 5:
            return "23" in secText[secText.index("24届") - 5 : secText.index("24届")]
        if "24年" in secText and secText.index("24年") >= 5:
            return "23" in secText[secText.index("24年") - 5 : secText.index("24年")]
        secBlackList1 = [
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
        return not any(item in secText for item in secBlackList1)
    except:
        return True


def checkTitle(titleText):
    try:
        titleText = titleText.lower()
        titleBlackList = [
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
            "人士",
            "管家",
        ]
        return not any(item in titleText for item in titleBlackList)
    except:
        return True


def checkCompany(companyText):
    try:
        companyBlackList = ["培训", "学校", "教育"]
        return not any(item in companyText for item in companyBlackList)
    except:
        return True


def checkRes():
    try:
        resElement = driver.find_element(By.CSS_SELECTOR, ".res-time")
        resText = resElement.text[-10:]
        dateFormat = "%Y-%m-%d"
        return time.mktime(time.strptime(resText, dateFormat)) < (
            time.time() - 31536000
        )
    except:
        return True


def isReadyToCommunicate(btnText):
    return "立即" in btnText


if not os.path.exists("resume.txt"):
    open("resume.txt", "w").close()
with open("resume.txt", "r") as file:
    for line in file:
        string = line.strip()
        if string not in resumesr:
            resumesr.add(string)
driver.get("https://www.zhipin.com/web/user/?ka=header-login")
WAIT.until(
    EC.presence_of_element_located(
        (By.CSS_SELECTOR, "[class*='btn-sign-switch ewm-switch']")
    )
)
driver.find_element(By.CSS_SELECTOR, "[class*='btn-sign-switch ewm-switch']").click()
time.sleep(20)
Query = [
    # "Java",
    "Java测试开发",
    "Java软件测试",
    "Java软件实施",
    "Java运维开发",
    "软件测试开发",
    "软件测试",
    "软件自动化测试",
    "软件功能测试",
    "Python软件测试",
    "软件实施",
    "后端开发",
    "软件开发",
    "全栈工程师",
    "软件需求分析",
    "软件性能测试",
    "Python",
    "Node.js",
    "数据分析",
    "数据挖掘",
    "DBA",
    "Hadoop",
    "JavaScript",
    "软件技术文档",
]
for i in range(1, 10):
    try:
        if resumeSubmission(URL1 + "Java" + URL2 + "404" + URL3 + str(i)) == -1:
            break
    except:
        continue
for i in range(1, 10):
    try:
        if resumeSubmission(URL1 + "Java" + URL2 + "403" + URL3 + str(i)) == -1:
            break
    except:
        continue
for item in Query:
    for i in range(1, 4):
        try:
            if resumeSubmission(URL1 + item + URL2 + "404" + URL3 + str(i)) == -1:
                break
        except:
            continue
    for i in range(1, 4):
        try:
            if resumeSubmission(URL1 + item + URL2 + "403" + URL3 + str(i)) == -1:
                break
        except:
            continue
driver.quit()
