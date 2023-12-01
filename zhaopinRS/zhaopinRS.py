import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
import undetected_chromedriver as uc

URL1 = "https://sou.zhaopin.com/?kw="
URL2 = "&p="
options = uc.ChromeOptions()
options.add_argument("--disable-popup-blocking")
options.add_argument("--disable-web-security")
options.add_argument("--disable-extensions")
driver = uc.Chrome(
    headless=False,
    user_data_dir=os.path.expanduser("~") + "/.config/google-chrome",
    options=options,
)
WAIT = WebDriverWait(driver, 20)


def search(url):
    for i in range(1, 10):
        driver.get(url + str(i))
        time.sleep(10)
        # 执行JavaScript代码来滚动到页面底部
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # 等待一段时间
        driver.implicitly_wait(5)
        resume()


def resume():
    time.sleep(1)
    for i in range(
        len(
            driver.find_elements(
                By.CSS_SELECTOR, "[class*='joblist-box__item clearfix']"
            )
        )
    ):
        try:
            title = driver.find_elements(
                By.CSS_SELECTOR, "[class*='iteminfo__line1__jobname__name']"
            )[i].text
            com = driver.find_elements(
                By.CSS_SELECTOR, "[class*='iteminfo__line1__compname__name']"
            )[i].text
            city = driver.find_elements(
                By.CSS_SELECTOR, "[class*='iteminfo__line2__jobdesc__demand__item']"
            )[3 * i].text
            experience = driver.find_elements(
                By.CSS_SELECTOR, "[class*='iteminfo__line2__jobdesc__demand__item']"
            )[3 * i + 1].text
            degree = driver.find_elements(
                By.CSS_SELECTOR, "[class*='iteminfo__line2__jobdesc__demand__item']"
            )[3 * i + 2].text
            salary = driver.find_elements(
                By.CSS_SELECTOR, "[class*='iteminfo__line2__jobdesc__salary']"
            )[i].text
            scale = driver.find_elements(
                By.CSS_SELECTOR, "[class*='iteminfo__line2__compdesc__item']"
            )[2 * i + 1].text
            if not (
                check_title(title)
                and check_company(com)
                and check_experience(experience)
                and check_city(city)
                and check_degree(degree)
                and check_salary(salary)
                and check_scale(scale)
            ):
                continue
            ActionChains(driver).move_to_element(
                driver.find_elements(
                    By.CSS_SELECTOR, "[class*='iteminfo__line1__jobname__name']"
                )[i]
            ).perform()
            if (
                "申请"
                in driver.find_elements(
                    By.CSS_SELECTOR, "[class*='a-job-apply-button']"
                )[i].text
            ):
                driver.find_elements(By.CSS_SELECTOR, "[class*='a-job-apply-button']")[
                    i
                ].click()
                time.sleep(5)
                driver.switch_to.window(driver.window_handles[0])
                time.sleep(5)
        except:
            pass


def check_salary(salary_text):
    """
    检查薪资
    """
    return "千" in salary_text


def check_scale(scale_text):
    """
    检查规模
    """
    return "以下" not in scale_text


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
        "通辽",
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
        "东华医为",
    ]
    return all(item not in company_text for item in company_blacks)


Query = [
    "java",
    "java软件开发",
    "软件测试",
    "软件实施",
    "java全栈工程师",
    "软件自动化测试",
    "软件功能测试",
    "java软件测试开发",
    "数据分析",
    "python软件测试",
]

for item in Query:
    search(URL1 + item + URL2)
driver.quit()
