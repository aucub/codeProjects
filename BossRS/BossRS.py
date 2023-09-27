import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL1 = "https://www.zhipin.com/web/geek/job?query="
URL2 = "&city=100010000&experience=102,101,103,104&degree=209,208,206,202,203&scale=303,304,305,306,302&salary="
URL3 = "&page="

driver = webdriver.Firefox()
WAIT = WebDriverWait(driver, 30)

def resumeSubmission(url):
    driver.get(url)
    time.sleep(15)
    WAIT.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='job-title clearfix']")))
    jobList = []
    jobElements = driver.find_elements(By.CSS_SELECTOR, "[class*='job-card-body clearfix']")
    for jobElement in jobElements:
            if(checkTitle(jobElement.find_element(By.CLASS_NAME, 'job-name').text) and checkCity(jobElement.find_element(By.CLASS_NAME, 'job-area').text) and checkCompany(jobElement.find_element(By.CLASS_NAME, 'company-name').find_element(By.TAG_NAME,'a').text) and checkIndustry(jobElement.find_element(By.CLASS_NAME, 'company-tag-list').find_element(By.TAG_NAME,'li').text) and isReadyToCommunicate(jobElement.find_element(By.CSS_SELECTOR,"[class*='job-info clearfix']").get_attribute('innerHTML'))):
                jobList.append(jobElement.find_element(By.CLASS_NAME, 'job-card-left').get_attribute("href"))
    for job in jobList:
        try:
            driver.get(job)
            WAIT.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='btn btn-startchat']")))
            btn = driver.find_element(By.CSS_SELECTOR, "[class*='btn btn-startchat']")
            print('开始检查')
            if not (checkActiveTime() and checkRes() and checkSec() and isReadyToCommunicate(btn.text)):
                print('检查异常')
                continue
            print('检查无异常')
            btn.click()
            WAIT.until(EC.presence_of_element_located((By.CLASS_NAME, "dialog-con")))
            dialogText = driver.find_element(By.CLASS_NAME, "dialog-con").text
            if "已达上限" in dialogText:
                return -1
            time.sleep(3)
        except:
            print('异常')
            pass
    return 0

def checkActiveTime():
    try:
        activeTimeElement = driver.find_element(By.CLASS_NAME, "boss-active-time")
        activeTimeText = activeTimeElement.text
        activeTimeBlackList = ["半年", "月内", "周内", "7日内", "本月","本周"]
        print('检查活跃时间'+activeTimeText)
        print(not any(item in activeTimeText for item in activeTimeBlackList))
        return not any(item in activeTimeText for item in activeTimeBlackList)
    except:
        print("检查活跃时间异常")
        return True

def checkCity(cityText):
    try:
        cityBlackList = ["沈阳", "乌鲁木齐", "乌兰察布", "大连", "哈尔滨", "呼和浩特"]
        return not any(item in cityText for item in cityBlackList)
    except:
        print("检查城市异常")
        return True

def checkIndustry(industryText):
    try:
        industryBlackList = ["培训","房产","经纪","中介"]
        return not any(item in industryText for item in industryBlackList)
    except:
        return True

def checkSec():
    try:
        secElement = driver.find_element(By.CLASS_NAME, "job-detail-section")
        secText = secElement.text.lower()
        KEYWORDS = ["java", "python", "spring", "sql", "linux", "j2ee", "web", "bug", "数据库", "后端", "软件测试","开发", "计算机", "编程"]
        if not any(item in secText for item in KEYWORDS):
            print("不包含关键词")
            return False
        secBlackList = ["不接受应届","日语", "精通c#", "node开发经验", "用户界面编程", "mcu", "dsp", "硬件控制", "上位"]
        if any(item in secText for item in secBlackList):
            print("包含黑名单")
            return False
        if "毕业时间" in secText:
            graduationTimeBlackList = ["2020","2021","2022"]
            graduationTime = secText[secText.index("毕业时间"):secText.index("毕业时间") + 15]
            if any(item in graduationTime for item in graduationTimeBlackList):
                print("毕业时间不符合要求")
                return False
        if "截止日期" in secText:
            try:
                expDateText=secText[secText.index("截止日期") + 5:secText.index("截止日期") + 15]
                dateFormat = "%Y.%m.%d"
                if time.mktime(time.strptime(expDateText, dateFormat)) < time.time():
                    print("截止日期不符合要求")
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
        print("检查职位描述异常")
        return True

def checkTitle(titleText):
    try:
        titleText=titleText.lower()
        titleBlackList = ["助教", "销售", "日", "员", "产品开发", "嵌入式开发", "单片机", "游戏", "电话", "选址", "外贸", "网络优化", "客服", "实验", "弱电", "电气", "ic", "硬件", "教师", "讲师", "推广", "培训", "残", "高级", "创业", "合伙", "光学", "顾问", "仿真", "cam"]
        return not any(item in titleText for item in titleBlackList)
    except:
        return True

def checkCompany(companyText):
    try:
        companyBlackList=["培训","学校","教育"]
        return not any(item in companyText for item in companyBlackList)
    except:
        return True

def checkRes():
    try:
        resElement = driver.find_element(By.CSS_SELECTOR, ".res-time")
        resText = resElement.text[-10:]
        dateFormat = "%Y-%m-%d"
        print("检查成立")
        print(time.mktime(time.strptime(resText, dateFormat)) < (time.time() - 31536000))
        return time.mktime(time.strptime(resText, dateFormat)) < (time.time() - 31536000)
    except:
        print("检查成立异常")
        return True

def isReadyToCommunicate(btnText):
    print('检查沟通:'+btnText)
    print("立即" in btnText)
    return "立即" in btnText

driver.get("https://www.zhipin.com/web/user/?ka=header-login")
WAIT.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='btn-sign-switch ewm-switch']")))
driver.find_element(By.CSS_SELECTOR, "[class*='btn-sign-switch ewm-switch']").click()
time.sleep(20)
Query = ["Java运维开发", "Java软件实施","Java软件测试", "Java测试开发", "Java",  "软件测试开发实施运维技术文档PythonLinux"]
for item in Query:
        for  i in range(1, 7):
            if resumeSubmission(URL1 +item+URL2+"404"+URL3 + str(i)) == -1:
                break
        for  i in range(1, 7):
            if resumeSubmission(URL1 +item+URL2+"403"+URL3 + str(i)) == -1:
                break
driver.quit()
