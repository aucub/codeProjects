import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "https://www.zhipin.com/web/geek/job?query=Java软件测试&city=100010000&experience=102,101,103,104&degree=209,208,206,202,203&scale=303,304,305,306,302&salary=404&page="

driver = webdriver.Firefox()
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
            if checkActiveTime() or checkSec() or checkTitle() or checkCompany() or checkCity() or checkIndustry() or checkRes() or not isReadyToCommunicate(btn):
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
    
def checkCity():
    try:
        cityElement = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[1]/div/div/div[1]/p/a")
        cityText = cityElement.text
        cityList = ["沈阳", "乌鲁木齐", "乌兰察布", "大连"]
        return any(item in cityText for item in cityList)
    except:
        return False

def checkIndustry():
    try:
        industryElement = driver.find_element(By.CSS_SELECTOR, ".sider-company > p:nth-child(5) > a:nth-child(2)")
        industryText = industryElement.text
        industryList = ["培训"]
        return any(item in industryText for item in industryList)
    except:
        return False

def checkSec():
    try:
        element = driver.find_element(By.CSS_SELECTOR, "div.job-detail-section:nth-child(1)")
        text = element.text.lower()
        KEYWORDS = ["java", "python", "spring", "sql", "linux", "j2ee", "web", "bug", "数据库", "后端", "软件测试", "开发", "计算机", "编程"]
        if not any(item in text for item in KEYWORDS):
            return True
        if "毕业时间" in text:
            graduationTime = text[text.index("毕业时间"):text.index("毕业时间") + 15]
            if "2020" in graduationTime or "2021" in graduationTime or "2022" in graduationTime:
                return True
        if "日语" in text or "精通c#" in text or "node开发经验" in text or "用户界面编程" in text or "mcu" in text or "dsp" in text or "硬件控制" in text or "上位" in text:
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
                print('计算截止日期')
                print('截止时间'+time.mktime(time.strptime(text[text.index("截止日期") + 5:text.index("截止日期") + 15], dateFormat)))
                return time.mktime(time.strptime(text[text.index("截止日期") + 5:text.index("截止日期") + 15], dateFormat)) < time.time()
            except:
                print('截止日期异常')
                print(text[text.index("截止日期") + 5:text.index("截止日期")+15])
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
        text = element.text.lower()
        return "助教" in text or "销售" in text or "日" in text or "员" in text or "产品开发" in text or "嵌入式开发" in text or "单片机" in text or "游戏" in text  or "电话" in text  or "选址" in text   or "外贸" in text or "网络优化" in text or "客服" in text or "实验" in text or "弱电" in text or "电气" in text or "ic" in text  or "硬件" in text or "教师" in text or "讲师" in text or "推广" in text or "培训" in text or "残" in text or "高级" in text or "创业" in text or "合伙" in text
    except:
        return False

def checkCompany():
    try:
        element = driver.find_element(By.CSS_SELECTOR, "div.company-info:nth-child(2) > a:nth-child(2)")
        text = element.text
        return "培训" in text or "学校" in text or "教育" in text
    except:
        return False
    
def checkRes():
    try:
        element = driver.find_element(By.CSS_SELECTOR, ".res-time")
        text = element.text[-10:]
        dateFormat = "%Y-%m-%d"
        return time.mktime(time.strptime(text, dateFormat)) > (time.time()-31536000)
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
