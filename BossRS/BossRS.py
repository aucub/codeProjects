import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "https://www.zhipin.com/web/geek/job?query=Java测试开发&city=100010000&experience=102,101,103,104&degree=209,208,206,202,203&scale=303,304,305,306,302&salary=403&page="

driver = webdriver.Firefox()
WAIT = WebDriverWait(driver, 30)

def resumeSubmission(url):
    driver.get(url)
    time.sleep(15)
    WAIT.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='job-title clearfix']")))
    jobList = []
    jobElements = driver.find_elements(By.CSS_SELECTOR, "[class*='job-card-left']")
    for jobElement in jobElements:
        jobList.append(jobElement.get_attribute("href"))
    for job in jobList:
        try:
            driver.get(job)
            WAIT.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='btn btn-startchat']")))
            btn = driver.find_element(By.CSS_SELECTOR, "[class*='btn btn-startchat']")
            if not (checkActiveTime() and checkSec() and checkTitle() and checkCompany() and checkCity() and checkIndustry() and checkRes() and isReadyToCommunicate(btn)):
                continue
            btn.click()
            WAIT.until(EC.presence_of_element_located((By.CLASS_NAME, "dialog-con")))
            dialogText = driver.find_element(By.CLASS_NAME, "dialog-con").text
            if "已达上限" in dialogText:
                return -1
            time.sleep(3)
        except:
            pass
    return 0

def checkActiveTime():
    try:
        activeTimeElement = driver.find_element(By.CSS_SELECTOR, "span.boss-active-time")
        activeTimeText = activeTimeElement.text
        activeTimeBlackList = ["半年前活跃", "半年内活跃", "近半年活跃", "月内活跃", "周内活跃", "7日内活跃", "本月活跃","本周活跃"]
        return not any(item in activeTimeText for item in activeTimeBlackList)
    except:
        return True

def checkCity():
    try:
        cityElement = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[1]/div/div/div[1]/p/a")
        cityText = cityElement.text
        cityBlackList = ["沈阳", "乌鲁木齐", "乌兰察布", "大连", "哈尔滨", "呼和浩特"]
        return not any(item in cityText for item in cityBlackList)
    except:
        return True

def checkIndustry():
    try:
        industryElement = driver.find_element(By.CSS_SELECTOR, ".sider-company > p:nth-child(5) > a:nth-child(2)")
        industryText = industryElement.text
        industryBlackList = ["培训"]
        return not any(item in industryText for item in industryBlackList)
    except:
        return True

def checkSec():
    try:
        secElement = driver.find_element(By.CSS_SELECTOR, "div.job-detail-section:nth-child(1)")
        secText = secElement.text.lower()
        KEYWORDS = ["java", "python", "spring", "sql", "linux", "j2ee", "web", "bug", "数据库", "后端", "软件测试",
                    "开发", "计算机", "编程"]
        if not any(item in secText for item in KEYWORDS):
            return False
        secBlackList = ["不接受应届","日语", "精通c#", "node开发经验", "用户界面编程", "mcu", "dsp", "硬件控制", "上位"]
        if any(item in secText for item in secBlackList):
            return False
        if "毕业时间" in secText:
            graduationTimeBlackList = ["2020","2021","2022"]
            graduationTime = secText[secText.index("毕业时间"):secText.index("毕业时间") + 15]
            if any(item in graduationTime for item in graduationTimeBlackList):
                return False
        if "截止日期" in secText:
            try:
                expDateText=secText[secText.index("截止日期") + 5:secText.index("截止日期") + 15]
                dateFormat = "%Y.%m.%d"
                if time.mktime(time.strptime(expDateText, dateFormat)) < time.time():
                    return False
            except:
                pass
        secList=["23届","23年","应届","应往届","毕业","0-1年", "0-2年", "0-3年"]
        if any(item in secText for item in secList):
            return True
        if "24届" in secText and secText.index("24届") >= 5:
            return "23" in secText[secText.index("24届") - 5:secText.index("24届")]
        if "24年" in secText and secText.index("24年") >= 5:
            return "23" in secText[secText.index("24年") - 5:secText.index("24年")]
        secBlackList1 = ["年以上", "年及以上", "年或以上", "1-2年", "1-3年", "1年-3年", "2-3年", "3-5年", "年(含)以上"]
        return not any(item in secText for item in secBlackList1)
    except:
        return True

def checkTitle():
    try:
        titleElement = driver.find_element(By.CSS_SELECTOR, "div.name:nth-child(2) > h1:nth-child(1)")
        titleText = titleElement.text.lower()
        titleBlackList = ["助教", "销售", "日", "员", "产品开发", "嵌入式开发", "单片机", "游戏", "电话", "选址", "外贸", "网络优化", "客服", "实验", "弱电", "电气", "ic", "硬件", "教师", "讲师", "推广", "培训", "残", "高级", "创业", "合伙", "光学", "顾问", "仿真", "cam"]
        return not any(item in titleText for item in titleBlackList)
    except:
        return True

def checkCompany():
    try:
        companyElement = driver.find_element(By.CSS_SELECTOR, "div.company-info:nth-child(2) > a:nth-child(2)")
        companyText = companyElement.text
        companyBlackList=["培训","学校","教育"]
        return not any(item in companyText for item in companyBlackList)
    except:
        return True

def checkRes():
    try:
        resElement = driver.find_element(By.CSS_SELECTOR, ".res-time")
        resText = resElement.text[-10:]
        dateFormat = "%Y-%m-%d"
        return time.mktime(time.strptime(resText, dateFormat)) < (time.time() - 31536000)
    except:
        return True

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
