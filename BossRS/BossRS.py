import json
import time
import re
import undetected_chromedriver as uc
from urllib.parse import urlparse, parse_qs
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

URL1 = "https://www.zhipin.com/web/geek/job?query="
URL2 = "&city=100010000&experience=102,101,103,104&scale=303,304,305,306,302&degree=209,208,206,202,203&salary="
URL3 = "&page="
URL4 = "https://www.zhipin.com/wapi/zpgeek/job/card.json?securityId="
URL5 = "&lid="
URL6 = "&sessionId="

driver = uc.Chrome(headless=False, version_main=119)
WAIT = WebDriverWait(driver, 30)


def resume_submission(url):
    try:
        driver.get(url)
        time.sleep(1)
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
            try:
                parsed_url = urlparse(url)
                query_params = parse_qs(parsed_url.query)
                lid = query_params.get("lid", [None])[0]
                security_id = query_params.get("securityId", [None])[0]
                driver.get(URL4 + security_id + URL5 + lid + URL6)
                time.sleep(0.5)
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
                    check_company(
                        driver.find_element(
                            By.CSS_SELECTOR,
                            "div.company-info:nth-child(2) > a:nth-child(2)",
                        ).text
                    )
                    and check_placeholder(
                        driver.find_element(
                            By.CSS_SELECTOR,
                            ".sider-company > p:nth-child(4)",
                        ).text
                    )
                    and check_experiece(
                        driver.find_element(
                            By.CSS_SELECTOR,
                            "span.text-desc:nth-child(2)",
                        ).text
                    )
                    and check_degree(
                        driver.find_element(
                            By.CSS_SELECTOR,
                            "span.text-desc:nth-child(3)",
                        ).text
                    )
                    and check_salary(
                        driver.find_element(
                            By.CSS_SELECTOR,
                            "span.salary",
                        ).text
                    )
                    and check_active_time(
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
                time.sleep(1)
            except:
                pass
        return 0
    except:
        return 0


def check_active_time(active_time_text):
    try:
        active_time_blacks = ["半年", "月内", "周内", "7日", "本月"]
        return not any(item in active_time_text for item in active_time_blacks)
    except:
        return True


def check_placeholder(placeholder_text):
    try:
        return "-20" not in placeholder_text
    except:
        return True


def check_experiece(experiece_text):
    try:
        return "5" not in experiece_text and "10" not in experiece_text
    except:
        return True


def check_degree(degree_text):
    try:
        return "硕" not in degree_text and "博" not in degree_text
    except:
        return True


def check_salary(salary_text):
    pattern = r"(\d+)-(\d+)K"
    match = re.search(pattern, salary_text)
    if match:
        low_salary = int(match.group(1))
        return low_salary < 10
    else:
        return True


def check_city(city_text):
    try:
        city_blacks = [
            "沈阳",
            "齐齐哈尔",
            "塔城",
            "长春",
            "毕节",
            "包头",
            "乌鲁木齐",
            "拉萨",
            "锡林",
            "葫芦",
            "乌兰察布",
            "大连",
            "哈尔滨",
            "呼和浩特",
            "鄂尔多斯",
        ]
        return not any(item in city_text for item in city_blacks)
    except:
        return True


def check_industry(industry_text):
    try:
        industry_blacks = ["培训", "教育", "院校", "房产", "经纪", "工程施工", "中介", "区块链"]
        return not any(item in industry_text for item in industry_blacks)
    except:
        return True


def check_sec(sec_text):
    try:
        if len(sec_text) < 55:
            return False
        sec_text = sec_text.lower()
        sec_keywords = [
            "java",
            "python",
            "c++",
            "spring",
            "sql",
            "linux",
            "j2ee",
            "web",
            "app",
            "bug",
            "数据库",
            "后端",
            "软件",
            "开发",
            "计算机",
            "编程",
        ]
        if not any(item in sec_text for item in sec_keywords):
            return False
        sec_blacks = [
            "不接受应届",
            "不考虑应届",
            "20-21年",
            "20年毕业",
            "22年及之前",
            "22年之前",
            "21年之前",
            "能直播",
            "保管与申购",
            "车模",
            "直播经验",
            "应届生勿",
            "日语",
            "精通c#",
            "精通lab",
            "node开发经验",
            "3年工作",
            "mcu",
            "dsp",
            "ecu",
            "uds",
            "cdd",
            "diva",
            "通过cet-6",
            "硬件测试",
            "整机测试",
            "设备及仪器",
            "蓝牙耳机",
            "游戏测试",
            "汽车",
            "车厂",
            "机器人",
            "硬件控制",
            "单片",
            "电机",
            "串口",
            "布线",
            "上位",
            "销售",
            "营销",
            "车间",
            "车型",
            "家具",
            "电路",
            "电气",
            "弱电",
            "变频",
            "plc",
            "pms",
            "配电",
            "电力",
            "电子工艺",
            "新材料",
            "物料",
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
            "电池",
            "给排水",
            "水利",
            "水务",
            "水文",
            "水资源",
            "化工",
            "石油",
            "土建",
            "进行培训",
            "安防产品",
            "手机厂商",
            "请勿联系",
            "兼职",
            "质检员",
            "退货",
            "水泵",
            "原标题",
            "软著",
            "课程",
            "老师",
            "家长",
            "样衣",
            "面辅料",
            "3d设计",
            "3d渲染",
            "犀牛软件",
            "三维建模",
            "频谱",
            "示波器",
            "万用表",
            "分析仪",
            "车载",
            "酷家乐",
            "面料",
            "女装",
            "全屋定制",
            "华广软件",
            "定制家具",
            "驻店设计师",
            "造诣软件",
            "网络交换机",
            "不是软件",
            "大学2字",
            "毕业3年",
            "毕业5年",
        ]
        if any(item in sec_text for item in sec_blacks):
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
        if "不支持在线" in sec_text or "线下面试" in sec_text:
            try:
                sec_Citys = ["上海", "苏州", "杭州"]
                if not any(
                    item
                    in driver.find_element(By.CLASS_NAME, "text-desc text-city").text
                    for item in sec_Citys
                ):
                    return False
            except:
                pass
        if "毕业时间" in sec_text:
            graduation_time_blacks = ["2020", "21", "22"]
            graduation_time = sec_text[
                sec_text.index("毕业时间") : sec_text.index("毕业时间") + 15
            ]
            if any(item in graduation_time for item in graduation_time_blacks):
                return False
            graduation_times = ["不限", "23"]
            if any(item in graduation_time for item in graduation_times):
                return True
        secs = ["23届", "23年", "往届", "0-1年", "0-2年", "0-3年"]
        if any(item in sec_text for item in secs):
            return True
        if "毕业时间" in sec_text:
            new_sec_text = (
                sec_text[: sec_text.index("毕业时间")]
                + sec_text[sec_text.index("毕业时间") + 15 :]
            )
        else:
            new_sec_text = sec_text
        if "24届" in new_sec_text or "24年" in new_sec_text:
            return "23" in sec_text
        secs1 = ["应届"]
        if any(item in sec_text for item in secs1):
            return True
        sec_blacks1 = [
            "年以上",
            "年及以上",
            "年或以上",
            "1-2年",
            "1-3年",
            "1至3年",
            "1年-3年",
            "2-3年",
            "2年左右",
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
            "单片机",
            "游戏",
            "电话",
            "选址",
            "外贸",
            "网络优化",
            "客服",
            "实验",
            "弱电",
            "消防",
            "暖通",
            "电气",
            "机电",
            "售前",
            "售后",
            "ic",
            "英文",
            "可靠",
            "仪器",
            "机械",
            "器械",
            "前端",
            "android",
            "蓝牙耳机",
            "相机",
            "耗材",
            "硬件",
            "教师",
            "讲师",
            "老师",
            "推广",
            "实训",
            "网络",
            "支持",
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
            "车",
            "主管",
            "经理",
            "基金",
            "三维",
            "芯片",
            "布料",
            ".net",
            "php",
            "市场",
            "obc",
            "高性能",
            "环保",
            "内部",
            "财务",
            "采购",
            "人士",
            "管家",
            "架构师",
            "水务",
            "棋牌",
            "组长",
            "英语",
            "渗透",
            "01",
            "资深",
            "专家",
            "兼职",
            "台湾",
            "海外",
            "c++",
            "实施运维",
            "实施",
            "运维",
            "shell",
            "电子",
            "驾驶",
            "c#",
            "win",
            "无人",
            "招聘",
            "高薪",
            "egp",
            "通信",
            "培养",
            "外派",
            "企点",
            "造价",
            "期刊",
            "玩具",
            "电动",
            "爬虫",
            "运营",
            "护士",
            "面料",
        ]
        return not any(item in title_text for item in title_blacks)
    except:
        return True


def check_company(company_text):
    try:
        company_blacks = ["培训", "学校", "人才", "教育"]
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
    "Java开发",
    "Java后端",
    "Java工程",
    "Java软件",
    "Java软件工程",
    "Java软件开发",
    "Java测试开发",
    "Java软件测试",
    "软件测试开发",
    "软件测试",
    "软件自动化测试",
    "软件功能测试",
    "Python软件测试",
    "Python测试",
    # "Java运维开发",
    # "Java软件实施",
    # "软件实施",
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
    for i in range(1, 15):
        try:
            if resume_submission(URL1 + item + URL2 + "404" + URL3 + str(i)) == -1:
                exit()
        except:
            continue
    for i in range(1, 15):
        try:
            if resume_submission(URL1 + item + URL2 + "403" + URL3 + str(i)) == -1:
                exit()
        except:
            continue
    for i in range(1, 15):
        try:
            if resume_submission(URL1 + item + URL2 + "402" + URL3 + str(i)) == -1:
                exit()
        except:
            continue
driver.quit()
