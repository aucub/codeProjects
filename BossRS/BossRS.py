import json
import os
import sys
import time
import re
import traceback
from urllib.parse import urlparse, parse_qs
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
import undetected_chromedriver as uc
from gpt import gpt

URL1 = "https://www.zhipin.com/web/geek/job?query="
URL2 = "&city=100010000&experience=101,102,103,104&scale=302,303,304,305,306&degree=209,208,206,202,203&salary="
URL3 = "&page="
URL4 = "https://www.zhipin.com/wapi/zpgeek/job/card.json?securityId="
URL5 = "&lid="
URL6 = "&sessionId="
URL7 = "&position="

driver = uc.Chrome(
    headless=False,
    user_data_dir=os.path.expanduser("~") + "/.config/google-chrome",
    version_main=120,
)
WAIT = WebDriverWait(driver, 15)


def resume_submission(url):
    """
    投递简历
    """
    driver.get(url)
    time.sleep(3)
    check_dialog()
    try:
        WAIT.until(
            ec.presence_of_element_located(
                (By.CSS_SELECTOR, "[class*='job-title clearfix']")
            )
        )
    except:
        traceback.print_exc()
        return 1
    jobs = []
    urls = []
    job_elements = driver.find_elements(
        By.CSS_SELECTOR, "[class*='job-card-body clearfix']"
    )
    for job_element in job_elements:
        if (
            check_title(job_element.find_element(By.CLASS_NAME, "job-name").text)
            and check_city(job_element.find_element(By.CLASS_NAME, "job-area").text)
            and check_company(
                job_element.find_element(By.CLASS_NAME, "company-name")
                .find_element(By.TAG_NAME, "a")
                .text
            )
            and check_industry(
                job_element.find_element(By.CLASS_NAME, "company-tag-list")
                .find_element(By.TAG_NAME, "li")
                .text
            )
            and is_ready_to_communicate(
                job_element.find_element(
                    By.CSS_SELECTOR, "[class*='job-info clearfix']"
                ).get_attribute("innerHTML")
            )
        ):
            urls.append(
                job_element.find_element(By.CLASS_NAME, "job-card-left").get_attribute(
                    "href"
                )
            )
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
            description = data["zpData"]["jobCard"]["postDescription"]
            active = data["zpData"]["jobCard"]["activeTimeDesc"]
            address = data["zpData"]["jobCard"]["address"]
            if not (
                check_sec(description)
                and check_active_time(active)
                and check_city(address)
            ):
                continue
        jobs.append(url)
    for job in jobs:
        driver.get(job)
        WAIT.until(
            ec.presence_of_element_located(
                (By.CSS_SELECTOR, "[class*='btn btn-startchat']")
            )
        )
        check_dialog()
        btn = driver.find_element(By.CSS_SELECTOR, "[class*='btn btn-startchat']")
        try:
            if not (
                check_company(
                    driver.find_element(
                        By.CSS_SELECTOR,
                        "div.company-info:nth-child(2) > a:nth-child(2)",
                    ).text
                )
                and check_guide(
                    driver.find_element(
                        By.CSS_SELECTOR, "[class*='pos-bread city-job-guide']"
                    ).text
                )
                and check_scale(
                    driver.find_element(
                        By.CSS_SELECTOR,
                        ".sider-company > p:nth-child(4)",
                    ).text
                )
                and check_experience(
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
                and check_res()
                and check_update(driver.find_element(By.CSS_SELECTOR, "p.gray").text)
                and check_sec(
                    driver.find_element(By.CLASS_NAME, "job-detail-section").text
                )
                and check_method(
                    driver.find_element(By.CLASS_NAME, "job-detail-section").text,
                    driver.find_element(
                        By.CSS_SELECTOR, "[class*='text-desc text-city']"
                    ).text,
                )
                and check_city(
                    driver.find_element(
                        By.CSS_SELECTOR, "[class*='location-address']"
                    ).text
                )
                and check_fund(
                    driver.find_element(By.CSS_SELECTOR, "[class*='company-fund']").text
                )
                and check_boss(
                    driver.find_element(By.CSS_SELECTOR, ".boss-info-attr").text
                )
                and is_ready_to_communicate(btn.text)
                and gpt.check(description)
            ):
                continue
        except:
            traceback.print_exc()
            continue
        try:
            if not (
                check_company(
                    driver.find_element(
                        By.CSS_SELECTOR,
                        "li.company-name",
                    ).text
                )
                and check_active_time(
                    driver.find_element(By.CLASS_NAME, "boss-active-time").text
                )
            ):
                continue
        except:
            traceback.print_exc()
            pass
        btn.click()
        check_dialog()
        time.sleep(5)
        try:
            WAIT.until(ec.presence_of_element_located((By.CLASS_NAME, "dialog-con")))
        except:
            traceback.print_exc()
            continue
        dialog_text = driver.find_element(By.CLASS_NAME, "dialog-con").text
        if "已达上限" in dialog_text:
            return -1
    return 0


def check_active_time(active_time_text):
    """
    检查活跃时间
    """
    active_time_blacks = ["半年", "月内", "周内", "本周", "7日", "本月"]
    return all(item not in active_time_text for item in active_time_blacks)


def check_scale(scale_text):
    """
    检查规模
    """
    return "-20" not in scale_text


def check_experience(experience_text):
    """
    检查经验
    """
    return "5" not in experience_text and "10" not in experience_text


def check_degree(degree_text):
    """
    检查学位
    """
    return "硕" not in degree_text and "博" not in degree_text


def check_fund(fund_text):
    """
    检查资金
    """
    if "-" in fund_text:
        return False
    lines = fund_text.splitlines()
    fund_text = lines[-1]
    fund_text = fund_text[:-3]
    fund_blacks = [
        "30万",
        "10万",
        "5万",
        "2万",
    ]
    return all(fund_text not in item for item in fund_blacks)


def check_salary(salary_text):
    """
    检查薪资
    """
    pattern = r"(\d+)-(\d+)K"
    match = re.search(pattern, salary_text)
    if match:
        low_salary = int(match.group(1))
        return low_salary < 9


def check_sec(sec_text):
    """
    检查职位描述
    """
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
    if all(item not in sec_text for item in sec_keywords):
        return False
    sec_blacks = [
        "式样书",
        "abview",
        "标书制作",
        "市场推广",
        "呼叫",
        "桌面运维",
        "仪器设备",
        "信号采集",
        "售后技术",
        "电话指导",
        "驾照",
        "三班倒",
        "红绿灯",
        "维护维修",
        "网络运维",
        "燃气",
        "热水器",
        "钣金",
        "模具",
        "样品",
        "贴片机",
        "机台",
        "验机",
        "大型设备",
        "路由器",
        "交换机",
        "卫星",
        "值班",
        "体育运动",
        "引体向上",
        "俯卧撑",
        "挖掘客户",
        "java勿扰",
        "没有编程",
        "不接受应届",
        "不接收应届",
        "不考虑应届",
        "应届生请勿",
        "20-21",
        "20年",
        "22年",
        "21年",
        "22应届",
        "20届",
        "咨询电话",
        "解答客户",
        "联系回访",
        "商机",
        "快手",
        "抖音",
        "陪产",
        "临床护理",
        "小红书",
        "反应堆",
        "测试组长",
        "嵌入式编程",
        "低功耗产品开发",
        "网络自动化",
        "网络规划设计",
        "运维通信",
        "能力稍逊",
        "资产登记",
        "电厂",
        "nbt200",
        "iec621",
        "请简述",
        "镭雕",
        "激光电视",
        "投影产品",
        "视频号",
        "开发客户",
        "智能手表",
        "夜班",
        "商务对接",
        "卫生工作",
        "城乡规划",
        "资源管理",
        "专利代理",
        "photoshop",
        "湘源",
        "sketchup",
        "财务",
        "会计",
        "审计",
        "财税",
        "能直播",
        "保管与申购",
        "车模",
        "直播经验",
        "应届生勿",
        "日语",
        "无线电",
        "嵌入式软件开发",
        "熟练使用c",
        "熟练掌握c",
        "内核裁剪",
        "驱动开发",
        "密码学",
        "证书管理",
        "ipsec",
        "vpn",
        "vpp",
        "sonic",
        "frr",
        "dpdk",
        "uboot",
        "洗衣机",
        "精通c#",
        "精通.net",
        "掌握c#",
        "会c#",
        "熟悉c#",
        "熟悉.net",
        "熟悉win",
        "熟悉wpf",
        "熟悉图像处理",
        "熟悉三维",
        "熟练运用c#",
        "熟练使用php",
        "爬虫经验",
        "算法经验",
        "熟练操作vb",
        "精通lab",
        "node开发经验",
        "qt语言基础",
        "xamarin",
        "mcu",
        "dicom",
        "visuallisp",
        "vba",
        "vs.net",
        "asp.net",
        "sfcs",
        "ads",
        "objectarx",
        "finereport",
        "dsp",
        "ecu",
        "uds",
        "cdd",
        "diva",
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
        "机顶盒",
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
        "限温",
        "水利",
        "水务",
        "水文",
        "水资源",
        "化工",
        "石油",
        "土建",
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
        "焊接",
        "电子元器件",
        "车载",
        "机房维护",
        "网络保障",
        "硬件运维",
        "酷家乐",
        "面料",
        "女装",
        "汽车行业",
        "墨滴",
        "喷射",
        "喷头",
        "材料化学",
        "机械制图",
        "喷墨",
        "供墨系统",
        "打印机",
        "首饰",
        "打板",
        "售后问题",
        "客情关系",
        "客户上门",
        "所属片区",
        "打字速度",
        "全屋定制",
        "华广软件",
        "定制家具",
        "驻店",
        "造诣软件",
        "交换机",
        "不是软件",
        "土木",
        "机械相关",
        "生产设备",
        "质检",
        "平面设计",
        "纺织",
        "无人机",
        "家纺",
        "会员群",
        "货品调配",
        "*****",
        "汇编",
        "产品开发专员",
        "大学2字",
        "暂挂",
        "简历收集",
        "非立即入职",
        "没有空缺",
        "天猫商家",
        "钉群管理",
        "电商开店",
        "外貌要求",
        "恕不退还",
        "已找到",
        "携带相关证件",
        "6级或以上",
        "211以上",
        "211本科以上",
        "211本科及以上",
    ]
    if any(item in sec_text for item in sec_blacks):
        return False
    if "截止日期" in sec_text:
        exp_date_text = sec_text[
            sec_text.index("截止日期") + 5 : sec_text.index("截止日期") + 15
        ]
        date_format = "%Y.%m.%d"
        try:
            if time.mktime(time.strptime(exp_date_text, date_format)) < time.time():
                return False
        except:
            traceback.print_exc()
            pass
    if "毕业时间" in sec_text:
        graduation_time_blacks = ["2020", "21", "22", "24年-"]
        graduation_time = sec_text[sec_text.index("毕业时间") : sec_text.index("毕业时间") + 15]
        if any(item in graduation_time for item in graduation_time_blacks):
            return False
        graduation_times = ["不限", "23"]
        if any(item in graduation_time for item in graduation_times):
            return True
    secs = ["23届", "23年", "24年及之前", "往届", "0-1年", "0-2年", "0-3年"]
    if any(item in sec_text for item in secs):
        return True
    if "截止日期" in sec_text:
        new_sec_text = (
            sec_text[: sec_text.index("截止日期")] + sec_text[sec_text.index("截止日期") + 15 :]
        )
    else:
        new_sec_text = sec_text
    if "24届" in new_sec_text or "24年" in new_sec_text or "24应届" in new_sec_text:
        return "23" in new_sec_text
    secs1 = ["应届"]
    if any(item in sec_text for item in secs1):
        return True
    sec_blacks1 = [
        "年以上",
        "在校生",
        "毕业前",
        "可实习至",
        "年及以上",
        "年或以上",
        "三年",
        "3年",
        "二年",
        "2年",
        "两年",
        "4年",
        "5年",
        "年(含)以上",
    ]
    return all(item not in sec_text for item in sec_blacks1)


def check_dialog():
    try:
        time.sleep(1)
        dialog_elements = driver.find_elements(By.CLASS_NAME, "dialog-container")
        if dialog_elements:
            driver.find_element(By.CLASS_NAME, "icon-close").click
        time.sleep(1)
    except:
        traceback.print_exc()


def check_res():
    """
    检查成立时间
    """
    try:
        res_element = driver.find_element(By.CSS_SELECTOR, ".res-time")
        res_text = res_element.text[-10:]
        date_format = "%Y-%m-%d"
        return time.mktime(time.strptime(res_text, date_format)) < (
            time.time() - 63072000
        )
    except:
        traceback.print_exc()
        return False


def check_update(update_text):
    """
    检查更新日期
    """
    update_text = update_text[-10:]
    date_format = "%Y-%m-%d"
    return time.mktime(time.strptime(update_text, date_format)) > (
        time.time() - 2592000
    )


def is_ready_to_communicate(btn_text):
    """
    检查能否沟通
    """
    return "立即" in btn_text


def check_city(city_text):
    """
    检查城市
    """
    city_blacks = [
        "沈阳",
        "辽阳",
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
        "大庆",
        "通辽",
        "大同",
        "哈尔滨",
        "呼和浩特",
        "鄂尔多斯",
        "西宁",
        "汉中",
        "沧州",
        "莆田",
        "伊犁",
        "布克",
        "塔城",
        "和丰",
        "喀什",
        "自治",
        "苗族",
        "黔",
        "兴义",
        "东营",
        "学院",
        "清远",
        "丹东",
        "海口",
        "烟台",
        "廊坊",
        "石家庄",
        "丽水",
        "平顶山",
    ]
    return all(item not in city_text for item in city_blacks)


def check_boss(boss_text):
    """
    检查人事
    """
    boss_text = boss_text.lower()
    boss_blacks = [
        "总裁",
        "总经理",
        "ceo",
        "创始人",
        "法人",
    ]
    return all(item not in boss_text for item in boss_blacks)


def check_method(sec_text, city_text):
    """
    检查面试方式
    """
    citys = ["上海", "苏州", "杭州", "南京"]
    secs = [
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
    if any(item in sec_text for item in secs):
        return any(item in city_text for item in citys)
    return True


def check_industry(industry_text):
    """
    检查行业
    """
    industry_blacks = [
        "培训",
        "教育",
        "院校",
        "房产",
        "经纪",
        "工程施工",
        "中介",
        "区块链",
        "批发",
        "零售",
        "再生资源",
    ]
    return all(item not in industry_text for item in industry_blacks)


def check_title(title_text):
    """
    检查标题
    """
    title_text = title_text.lower()
    title_blacks = [
        "产品",
        "支持",
        "调试",
        "机器视觉",
        "非开发",
        "验证",
        "笔电",
        "结构",
        "衡器",
        "dqe",
        "厂区",
        "轻松",
        "运营助理",
        "顾问",
        "亚马逊",
        "专利",
        "代理",
        "外包",
        "舆情",
        "处理",
        "生产",
        "服务",
        "嵌入式软件开发",
        "装备",
        "助教",
        "销售",
        "日",
        "员",
        "设备",
        "陪产",
        "现场",
        "单片机",
        "测评",
        "游戏",
        "电话",
        "选址",
        "外贸",
        "网络",
        "客服",
        "实验",
        "弱电",
        "消防",
        "暖通",
        "电气",
        "机电",
        "售前",
        "售后",
        "二维",
        "动画",
        "ic",
        "英文",
        "可靠",
        "仪器",
        "机械",
        "器械",
        "前端",
        "android",
        "wpf",
        "耳机",
        "相机",
        "耗材",
        "硬件",
        "教师",
        "讲师",
        "老师",
        "推广",
        "实训",
        "经营",
        "对账",
        "网络",
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
        "架构",
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
        "香港",
        "海外",
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
        "粤语",
        "内窥",
        "维修",
        "视频",
        "文件管理",
        "惠普",
        "速卖通",
        "营销",
        "经销",
        "城市规划",
        "质检",
        "回收",
        "手机",
        "无人机",
        "小白",
        "设计",
        "收银",
        "金融",
        "node",
        "qt",
        "界面",
        "前端",
        "数据质量",
        "数据标注",
        "c语言开发",
        "bim",
        "cad",
        "go",
        "安卓",
        "项目管理",
        "管理",
        "电商",
        "算法",
        "商务",
        "审计",
        "样品",
        "小程序开发",
        "数据库研发",
        "开发媒介",
        "25",
    ]
    return all(item not in title_text for item in title_blacks)


def check_guide(guide_text):
    """
    检查导航
    """
    guide_text = guide_text.lower()
    guide_blacks = [
        "地产中介",
        "销售",
        "采购",
        "电梯工",
        "药剂",
        "教师",
        "电气",
        "焊工",
        "前厅",
        "酒店",
        "广告制作",
        "配送",
        "摄影",
        "摄像",
        "水电",
        "制片",
    ]
    return all(item not in guide_text for item in guide_blacks)


def check_company(company_text):
    """
    检查公司名称
    """
    company_blacks = [
        "顺丰集团",
        "精仪精测",
        "昌硕科技",
        "腾云悦智",
        "新疆",
        "乌鲁木齐",
        "大连",
        "京北方",
        "辛可必",
        "微创软件",
        "企业管理",
        "信息咨询",
        "美婷",
        "富联富桂",
        "培训",
        "职业",
        "中介",
        "学校",
        "人才",
        "人力",
        "劳务",
        "教育",
        "童星",
        "儿童",
        "童画",
        "工艺",
        "青萍",
        "喜悦",
        "快服",
        "索勤",
        "京隆",
        "派森特",
        "久远银海",
        "博彦",
        "沐雨禾禾",
        "农业",
        "华迅网络",
        "中电金信",
        "中软国际",
        "蓝鸽",
        "nio",
        "谐云",
        "广日电梯",
        "压寨",
        "合伙",
        "中科软",
        "汉科软",
        "快酷",
        "拓尔思",
        "奥特",
        "平云",
        "原子云",
        "泛微",
        "创业",
        "神州",
        "平安",
        "天有为",
        "天地伟业",
        "图墨",
        "易科士",
        "老乡鸡",
        "货拉拉",
        "新点软件",
        "视源",
        "博为峰",
        "美淘淘",
        "软通动力",
        "麦田房产",
        "招商银行",
        "格林豪泰",
        "佰钧成",
        "我爱我家",
        "地产",
        "宸鸿",
        "华众万象",
        "棱镜网络",
        "丹迪兰",
        "法本",
        "劲爆",
        "天玑科技",
        "华众科技",
        "百思科技",
        "网新恒天",
        "致成电子",
        "绣歌",
        "神玥",
        "通力互联",
        "北京银行",
        "房产",
        "房屋",
        "销售",
        "投资咨询",
        "咨询管理",
        "品牌",
        "再生资源",
        "玻璃",
        "教育咨询",
        "教育信息咨询",
        "文化传播",
        "文化传承",
        "文化传媒",
        "营销",
        "策划",
        "经纪",
        "珠宝",
        "旅馆",
        "餐厅",
        "宾馆",
        "摄影",
        "啦啦",
        "旅游开发",
        "法律咨询",
        "文艺创作",
        "水处理",
        "材料",
        "合作社",
        "汽车",
        "婚纱",
        "信用卡",
        "维修",
        "轿车",
        "尔希",
        "名人",
        "演员",
        "钟表",
        "网吧",
        "注册",
        "托管",
        "美嘉林",
        "海绵",
        "家居",
        "担保",
        "养殖",
        "汽修",
        "塑料",
        "餐饮",
        "面包房",
        "艺术",
        "蛋糕",
        "调味品",
        "小吃",
        "早教",
        "宠物",
        "车载",
        "管理咨询",
        "保险",
        "装饰",
        "电热",
        "火箭",
        "农场",
        "假日",
        "园艺",
        "环境工程",
        "代理",
        "练字",
        "书法",
        "书画",
        "器材",
        "烘培",
        "服饰",
        "焊业",
        "歌城",
        "美容",
        "投资",
        "少儿",
        "美术",
        "门窗",
        "人力市场",
        "信用管理",
        "建材",
        "机械制造",
        "模具",
        "建筑工程",
        "配件",
        "服装",
        "健身",
        "化妆",
        "美颜",
        "加盟",
        "皇家",
        "花苑",
        "舞蹈",
        "农产品",
        "小镇",
        "直营",
        "托育",
        "工会",
        "练习",
        "店",
        "宏源电子",
        "室",
        "馆",
        "行",
        "鞋业",
        "鞋厂",
        "叮咚",
        "卓杭",
        "商场",
        "商行",
        "经营部",
        "工作室",
        "企企通",
        "策马科技",
        "任拓",
        "东华软件",
        "东华医为",
    ]
    return all(item not in company_text for item in company_blacks)


# driver.get("https://www.zhipin.com/web/user/?ka=header-login")
# WAIT.until(
#     ec.presence_of_element_located(
#         (By.CSS_SELECTOR, "[class*='btn-sign-switch ewm-switch']")
#     )
# )
# driver.find_element(By.CSS_SELECTOR, "[class*='btn-sign-switch ewm-switch']").click()
# WAIT.until(ec.url_changes(driver.current_url))

Query = [
    "Java",
    "Java软件开发",
    "软件测试",
    "软件自动化测试",
    "软件功能测试",
    "软件性能测试",
    # "软件测试开发",
    # "软件实施",
    # "全栈工程师",
    # "数据分析",
    # "数据挖掘",
    # "Python",
    # "软件需求分析",
    # "Node.js",
    # "DBA",
    # "Hadoop",
    # "JavaScript",
    # "软件技术文档",
]
for item in Query:
    for salary in ["404", "403", "402"]:
        for i in range(1, 15):
            if resume_submission(URL1 + item + URL2 + salary + URL3 + str(i)) == -1:
                sys.exit()
POSITION = [
    "Java" + URL7 + "100101",  # Java
    "Java" + URL7 + "100305",  # 测试开发
    URL7 + "100309",  # 软件测试
    "软件测试" + URL7 + "100301",  # 测试工程师
    "软件测试" + URL7 + "100302",  # 自动化测试
    "软件测试" + URL7 + "100303",  # 功能测试
    "Java" + URL7 + "100402",  # 运维开发
    "Java" + URL7 + "100606",  # 实施
    "Java" + URL7 + "100123",  # 全栈工程师
    # URL7 + "100123",  # 全栈工程师
    # "软件运维开发" + URL7 + "100402",  # 运维开发
    # "软件运维" + URL7 + "100401",  # 运维
]
for item in POSITION:
    for salary in ["404", "403", "402"]:
        for i in range(1, 15):
            if resume_submission(URL1 + item + URL2 + salary + URL3 + str(i)) == -1:
                sys.exit()
driver.quit()
