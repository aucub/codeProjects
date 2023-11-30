import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementClickInterceptedException
import undetected_chromedriver as uc

URL1 = "https://we.51job.com/pc/search?keyword="
URL2 = "&searchType=2&sortType=0&metro="
driver = uc.Chrome(
    headless=False,
    user_data_dir="/home/uymi/.config/google-chrome-beta",
)
WAIT = WebDriverWait(driver, 20)


def search(url):
    driver.get(url)
    time.sleep(60)
    WAIT.until(EC.element_to_be_clickable((By.CLASS_NAME, "carrybox")))
    driver.find_element(By.CLASS_NAME, "carrybox").click()
    clist = driver.find_elements(By.CLASS_NAME, "clist")
    # 薪资
    driver.find_element(
        By.CSS_SELECTOR,
        "#app > div > div.post > div > div > div:nth-child(1) > div.j_filter > div:nth-child(2) > div > div.mt.mt_sal",
    ).click()
    clist[1].find_elements(By.CLASS_NAME, "ch")[7].click()
    clist[1].find_elements(By.CLASS_NAME, "ch")[6].click()
    clist[1].find_elements(By.CLASS_NAME, "ch")[5].click()
    clist[1].find_elements(By.CLASS_NAME, "ch")[4].click()
    clist[1].find_elements(By.CLASS_NAME, "ch")[3].click()
    driver.find_element(
        By.CSS_SELECTOR,
        "#app > div > div.post > div > div > div:nth-child(1) > div.j_filter > div:nth-child(2) > div > div.btnbox > div > span:nth-child(1)",
    ).click()
    time.sleep(10)
    # 年限
    driver.find_element(
        By.CSS_SELECTOR,
        "#app > div > div.post > div > div > div:nth-child(1) > div.j_filter > div.launchbox.open > div:nth-child(1) > div > div.mt.mt_sal",
    ).click()
    clist[2].find_elements(By.CLASS_NAME, "ch")[1].click()
    clist[2].find_elements(By.CLASS_NAME, "ch")[2].click()
    clist[2].find_elements(By.CLASS_NAME, "ch")[6].click()
    driver.find_element(
        By.CSS_SELECTOR,
        "#app > div > div.post > div > div > div:nth-child(1) > div.j_filter > div.launchbox.open > div:nth-child(1) > div > div.btnbox > div > span:nth-child(1)",
    ).click()
    time.sleep(10)
    # 学历
    driver.find_element(
        By.CSS_SELECTOR,
        "#app > div > div.post > div > div > div:nth-child(1) > div.j_filter > div.launchbox.open > div:nth-child(2) > div > div.mt.mt_sal",
    ).click()
    clist[3].find_elements(By.CLASS_NAME, "ch")[1].click()
    clist[3].find_elements(By.CLASS_NAME, "ch")[2].click()
    clist[3].find_elements(By.CLASS_NAME, "ch")[3].click()
    clist[3].find_elements(By.CLASS_NAME, "ch")[4].click()
    clist[3].find_elements(By.CLASS_NAME, "ch")[7].click()
    driver.find_element(
        By.CSS_SELECTOR,
        "#app > div > div.post > div > div > div:nth-child(1) > div.j_filter > div.launchbox.open > div:nth-child(2) > div > div.btnbox > div > span:nth-child(1)",
    ).click()
    time.sleep(10)
    # 规模
    driver.find_element(
        By.CSS_SELECTOR,
        "#app > div > div.post > div > div > div:nth-child(1) > div.j_filter > div.launchbox.open > div:nth-child(4) > div > div.mt.mt_sal",
    ).click()
    clist[5].find_elements(By.CLASS_NAME, "ch")[3].click()
    clist[5].find_elements(By.CLASS_NAME, "ch")[4].click()
    clist[5].find_elements(By.CLASS_NAME, "ch")[5].click()
    clist[5].find_elements(By.CLASS_NAME, "ch")[6].click()
    clist[5].find_elements(By.CLASS_NAME, "ch")[7].click()
    driver.find_element(
        By.CSS_SELECTOR,
        "#app > div > div.post > div > div > div:nth-child(1) > div.j_filter > div.launchbox.open > div:nth-child(4) > div > div.btnbox > div > span:nth-child(1)",
    ).click()
    time.sleep(10)
    # 最新排序
    driver.find_elements(By.CLASS_NAME, "ss")[1].click()
    # 发布日期
    driver.find_element(By.CSS_SELECTOR, "div.op:nth-child(2)").click()
    driver.find_element(By.CSS_SELECTOR, "p.pp:nth-child(3) > a:nth-child(1)").click()
    time.sleep(10)

    for i in range(1, 16):
        WAIT.until(EC.presence_of_element_located((By.CLASS_NAME, "mytxt")))
        driver.find_element(By.CLASS_NAME, "mytxt").clear()
        driver.find_element(By.CLASS_NAME, "mytxt").send_keys(str(i))
        driver.find_element(By.CLASS_NAME, "jumpPage").click()
        resume()
        time.sleep(5)


def resume():
    time.sleep(1)
    job = 0
    for i in range(
        len(
            driver.find_elements(
                By.CSS_SELECTOR, "[class*='joblist-item sensors_exposure']"
            )
        )
    ):
        try:
            print(i)
            title = driver.find_elements(By.CSS_SELECTOR, "[class*='jname text-cut']")[
                i
            ].text
            com = driver.find_elements(By.CSS_SELECTOR, "[class*='cname text-cut']")[
                i
            ].text
            cut = driver.find_elements(By.CLASS_NAME, "area")[i].text
            dcut = driver.find_elements(By.CSS_SELECTOR, "[class*='dc text-cut']")[
                i
            ].text
            print(title)
            print(com)
            print(cut)
            print(dcut)
            if not (
                check_title(title)
                and check_company(com)
                and check_industry(dcut)
                and check_city(cut)
            ):
                continue
            element = driver.find_elements(By.CSS_SELECTOR, "[class*='ick']")[i]
            ActionChains(driver).move_to_element(element).click().perform()
            job = job + 1
        except:
            pass
    # 批量申请
    if job == 0:
        return
    else:
        success = False
    while not success:
        try:
            element = driver.find_elements(By.CSS_SELECTOR, "[class*='p_but']")[2]
            # 模拟鼠标点击
            ActionChains(driver).move_to_element(element).click().perform()
            success = True
        except ElementClickInterceptedException:
            time.sleep(1)
    time.sleep(5)
    # 处理弹窗
    text = WAIT.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "[class*='van-popup van-popup--center']")
        )
    ).text
    # 关闭弹窗
    driver.find_element(
        By.CSS_SELECTOR,
        "[class*='van-icon van-icon-cross van-popup__close-icon van-popup__close-icon--top-right']",
    ).click()


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
    ]
    return all(item not in city_text for item in city_blacks)


def check_title(title_text):
    """
    检查标题
    """
    title_text = title_text.lower()
    title_blacks = [
        "运营助理",
        "咨询顾问",
        "亚马逊",
        "专利",
        "代理",
        "驻点",
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
        "蓝牙耳机",
        "相机",
        "耗材",
        "硬件",
        "教师",
        "讲师",
        "老师",
        "推广",
        "实训",
        "经营分析",
        "对账",
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
        "香港",
        "海外",
        "c++",
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
        "粤语",
        "内窥镜",
        "维修",
        "视频",
        "文件管理",
        "结构设计",
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
        "产品开发",
        "开发媒介",
        "24",
        "25",
    ]
    return all(item not in title_text for item in title_blacks)


def check_company(company_text):
    """
    检查公司名称
    """
    company_blacks = [
        "新疆",
        "乌鲁木齐",
        "培训",
        "职业",
        "中介",
        "学校",
        "人才",
        "人力",
        "人力资源",
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
        "掌趣",
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
        "链家房地产",
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
        "酒店管理",
        "北京银行",
        "房地产",
        "房产",
        "房屋",
        "太平洋房屋",
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
        "酒店",
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
        "比萨店",
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
        "财务代理",
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
        "快餐店",
        "人力市场",
        "信用管理",
        "建材",
        "机械制造",
        "模具",
        "便利店",
        "饮品店",
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
    ]
    return all(item not in company_text for item in company_blacks)


# driver.get(
#     "https://login.51job.com/login.php?loginway=0&isjump=0&lang=c&from_domain=i&url=http%3A%2F%2Fwww.51job.com%2F&zhidinginfo="
# )
# time.sleep(50)

Query = [
    "java",
    "java软件开发",
    "软件测试",
    "软件实施",
    "全栈工程师",
    "软件自动化测试",
    "软件功能测试",
    "软件性能测试",
    "软件测试开发",
    "数据分析",
    "Python",
]

for item in Query:
    search(URL1 + item + URL2)
