import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

BASE_URL = "https://www.zhipin.com/web/geek/job?query=软件测试&city=100010000&experience=102,101,103,104&degree=209,208,206,202,203&scale=303,304,305,306,302&salary=404&page="

driver = webdriver.Chrome()
WAIT = WebDriverWait(driver,30)

def resumeSubmission(url):
    driver.get(url)
    time.sleep(15)
    WAIT.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='job-title clearfix']")))
    list = []
    elements = driver.find_elements(By.CSS_SELECTOR, "[class*='job-card-left']")
    for element in elements:
        list.append(element.get_attribute("href"))
    for s in list:
        try:
            driver.get(s)
            WAIT.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='btn btn-startchat']")))
            btn = driver.find_element(By.CSS_SELECTOR, "[class*='btn btn-startchat']")
            if checkActiveTime() or checkGraduationYear() or checkTitle() or checkCompany() or not isReadyToCommunicate(btn):
                continue
            btn.click()
            WAIT.until(EC.presence_of_element_located((By.CLASS_NAME, "dialog-con")))
            text = driver.find_element(By.CLASS_NAME, "dialog-con").text
            if "已达上限" in text:
                return -1
            time.sleep(3)
        except:
            pass
    return 0

def checkActiveTime():
    try:
        activeTimeElement = driver.find_element(By.CSS_SELECTOR, "span.boss-active-time")
        activeTimeText = activeTimeElement.text
        activeTimeList = ["半年前活跃", "半年内活跃", "近半年活跃", "月内活跃", "周内活跃","7日内活跃", "本月活跃", "本周活跃"]
        return any(item in activeTimeText for item in activeTimeList)
    except:
        return False

def checkGraduationYear():
    try:
        element = driver.find_element(By.CSS_SELECTOR, ".job-sec-text")
        text = element.text
        lowerCaseText = text.lower()
        KEYWORDS = ["java", "python", "spring", "sql", "linux", "j2ee", "web", "bug", "数据库", "后端", "软件测试", "开发", "计算机", "编程"]
        if not any(item in lowerCaseText for item in KEYWORDS):
            return True
        if "毕业时间" in text:
            graduationTime = text[text.index("毕业时间"):text.index("毕业时间") + 15]
            if "2020" in graduationTime or "2021" in graduationTime or "2022" in graduationTime:
                return True
        if "日语" in text:
            return True
        if "23届" in text or "23年" in text:
            return False
        if "24届" in text and text.index("24届") >= 5:
            return "23" not in text[text.index("24届") - 5:text.index("24届")]
        if "24年" in text and text.index("24年") >= 5:
            return "23" not in text[text.index("24年") - 5:text.index("24年")]
        if "截止日期" in text:
            try:
                dateFormat = "%Y.%m.%d"
                return datetime.strptime(text[text.index("截止日期") + 5:text.index("截止日期") + 15], dateFormat) < datetime.now()
            except:
                pass
        if "不接受应届" in text:
            return True
        if "应届" in text or "应往届" in text or "毕业" in text:
            return False
        if "0-1年" in text or "0-2年" in text or "0-3年" in text:
            return False
        return "年以上" in text or "年及以上" in text or "年或以上" in text or "1-2年" in text or "1-3年" in text or "1年-3年" in text or "2-3年" in text or "3-5年" in text or "年(含)以上" in text
    except:
        return False

def checkTitle():
    try:
        element = driver.find_element(By.CSS_SELECTOR, "div.name:nth-child(2) > h1:nth-child(1)")
        text = element.text
        return "助教" in text or "销售" in text or "日" in text or "游戏" in text or "实验" in text or "弱电" in text  or "IC" in text  or "硬件" in text or "教师" in text or "讲师" in text or "推广" in text or "培训" in text or "残" in text or "高级" in text
    except:
        return False

def checkCompany():
    try:
        element = driver.find_element(By.CSS_SELECTOR, "div.company-info:nth-child(2) > a:nth-child(2)")
        text = element.text
        return "培训" in text or "学校" in text or "教育" in text
    except:
        return False

def isReadyToCommunicate(btn):
    return btn.text == "立即沟通"

driver.get("https://www.zhipin.com/web/user/?ka=header-login")
WAIT.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='btn-sign-switch ewm-switch']")))
driver.find_element(By.CSS_SELECTOR, "[class*='btn-sign-switch ewm-switch']").click()
time.sleep(20)
for i in range(1, 7):
    if resumeSubmission(BASE_URL + str(i)) == -1:
        break
driver.quit()
