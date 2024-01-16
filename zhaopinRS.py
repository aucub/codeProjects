import os
import time
import traceback
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
import undetected_chromedriver as uc

URL1 = "https://sou.zhaopin.com/?kw="
URL2 = "&p="
options = uc.ChromeOptions()
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
            title = driver.find_elements(By.CSS_SELECTOR, "[class*='jobinfo__name']")[
                i
            ].text
            com = driver.find_elements(By.CSS_SELECTOR, "[class*='companyinfo__name']")[
                i
            ].text
            city = driver.find_elements(
                By.CSS_SELECTOR, "[class*='jobinfo__other-info-item']"
            )[3 * i].text
            experience = driver.find_elements(
                By.CSS_SELECTOR, "[class*='jobinfo__other-info-item']"
            )[3 * i + 1].text
            degree = driver.find_elements(
                By.CSS_SELECTOR, "[class*='jobinfo__other-info-item']"
            )[3 * i + 2].text
            salary = driver.find_elements(
                By.CSS_SELECTOR, "[class*='jobinfo__salary']"
            )[i].text
            scale = driver.find_elements(
                By.CSS_SELECTOR, "[class*='companyinfo__tag']"
            )[i].text
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
                    By.CSS_SELECTOR, "[class*='joblist-box__item clearfix']"
                )[i].find_elements(By.CSS_SELECTOR, "[class*='a-job-apply-button']")[0]
            ).perform()
            if (
                "申请"
                in driver.find_elements(
                    By.CSS_SELECTOR, "[class*='joblist-box__item clearfix']"
                )[i]
                .find_elements(By.CSS_SELECTOR, "[class*='a-job-apply-button']")[0]
                .text
            ):
                driver.find_elements(
                    By.CSS_SELECTOR, "[class*='joblist-box__item clearfix']"
                )[i].find_elements(By.CSS_SELECTOR, "[class*='a-job-apply-button']")[
                    0
                ].click()
                time.sleep(5)
                driver.switch_to.window(driver.window_handles[0])
                time.sleep(7)
        except Exception:
            traceback.print_exc()
            pass
    all_handles = driver.window_handles
    current_handle = driver.current_window_handle
    for handle in all_handles:
        if handle != current_handle:
            driver.switch_to.window(handle)
            driver.close()
    driver.switch_to.window(current_handle)


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
        "辽宁",
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
        "丽水",
        "平顶山",
    ]
    return all(item not in city_text for item in city_blacks)


def check_title(title_text):
    """
    检查标题
    """
    title_text = title_text.lower()
    title_blacks = [
        "可靠",
        "光源",
        "打光",
        "梳理",
        "材料",
        "预结算",
        "安装",
        "检测",
        "轮班",
        "倒班",
        "夜班",
        "保洁",
        "酒店",
        "监控",
        "声音",
        "设备",
        "党建",
        "宣传",
        "招聘",
        "人事",
        "质控",
        "手机检测",
        "产品助理",
        "项目助理",
        "人事助理",
        "桌面运维",
        "开发专员",
        "安卓开发",
        "上门",
        "aoi",
        "n2",
        "leader",
        "整机",
        "笔电",
        "结构",
        "衡器",
        "dqe",
        "厂区",
        "轻松",
        "运营助理",
        "亚马逊",
        "专利",
        "代理",
        "舆情",
        "处理",
        "生产",
        "装备",
        "助教",
        "销售",
        "日",
        "陪产",
        "量化",
        "统计",
        "商务",
        "服装",
        "选址",
        "外贸",
        "实验",
        "弱电",
        "食品",
        "学徒",
        "前台",
        "导购",
        "消防",
        "暖通",
        "电气",
        "机电",
        "售前",
        "售后",
        "二维",
        "动画",
        "仪器",
        "机械",
        "器械",
        "耗材",
        "硬件",
        "教师",
        "讲师",
        "餐饮",
        "必胜客",
        "人力",
        "文员",
        "机房",
        "农业",
        "林业",
        "直播",
        "老师",
        "推广",
        "测量",
        "操作工",
        "病理",
        "元器件",
        "技术员",
        "实训",
        "经营",
        "对账",
        "培训",
        "训练",
        "残",
        "创业",
        "合伙",
        "光学",
        "座舱",
        "车",
        "经理",
        "基金",
        "三维",
        "芯片",
        "布料",
        "市场",
        "obc",
        "环保",
        "财务",
        "采购",
        "人士",
        "管家",
        "水务",
        "棋牌",
        "资深",
        "专家",
        "兼职",
        "台湾",
        "香港",
        "海外",
        "驾驶",
        "无人",
        "高薪",
        "egp",
        "通信",
        "外派",
        "企点",
        "造价",
        "期刊",
        "玩具",
        "电动",
        "运营",
        "发单",
        "护士",
        "面料",
        "粤语",
        "内窥",
        "装修",
        "家装",
        "施工",
        "税务",
        "图像",
        "设计师",
        "生信",
        "室内",
        "行政",
        "客服",
        "拍摄",
        "剪辑",
        "理疗",
        "美容",
        "数据员",
        "制图员",
        "调测员",
        "新媒体",
        "道路",
        "安防",
        "展厅",
        "买手",
        "微信",
        "数通",
        "维修",
        "打单",
        "单证",
        "节目",
        "智库",
        "法务",
        "部门",
        "资料",
        "分诊",
        "录入",
        "签证",
        "物流",
        "标注",
        "建筑",
        "惠普",
        "速卖通",
        "电商助理",
        "营销",
        "经销",
        "城市规划",
        "质检",
        "回收",
        "无人机",
        "小白",
        "收银",
        "bim",
        "caxa",
        "跟线",
        "管理",
        "审计",
        "样品",
        "组长",
        "主管",
        "高级",
        "渗透",
        "爬虫",
        "网络",
        "游戏",
        "架构",
        "英文",
        "英语",
        "单片机",
        "嵌入式软件开发",
        "qt",
        "unity",
        "ue4",
        "ue5",
        "3d",
        ".net",
        "php",
        "wpf",
        "开发媒介",
        "c语言开发",
        "c++软件开发",
        "前端开发",
        "python开发",
        "go",
        "算法",
        "c#",
    ]
    return all(item not in title_text for item in title_blacks)


def check_company(company_text):
    """
    检查公司名称
    """
    company_blacks = [
        "乌鲁木齐",
        "京北方",
        "辛可必",
        "信息咨询",
        "美婷",
        "富联富桂",
        "培训",
        "职业",
        "中介",
        "学校",
        "人力",
        "童星",
        "儿童",
        "童画",
        "童美",
        "工艺",
        "青萍",
        "喜悦",
        "派森特",
        "沐雨禾禾",
        "中电金信",
        "广日电梯",
        "压寨",
        "合伙",
        "中科软",
        "汉科软",
        "快酷",
        "奥特",
        "原子云",
        "泛微",
        "创业",
        "图墨",
        "易科士",
        "老乡鸡",
        "美淘淘",
        "麦田房产",
        "招商银行",
        "格林豪泰",
        "佰钧成",
        "我爱我家",
        "地产",
        "宸鸿",
        "华众万象",
        "丹迪兰",
        "劲爆",
        "天玑科技",
        "华众科技",
        "百思科技",
        "绣歌",
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
        "文化传承",
        "文化传媒",
        "经纪",
        "旅馆",
        "餐厅",
        "宾馆",
        "摄影",
        "啦啦",
        "旅游开发",
        "法律咨询",
        "文艺创作",
        "水处理",
        "合作社",
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
        "面包房",
        "艺术",
        "蛋糕",
        "调味品",
        "小吃",
        "早教",
        "宠物",
        "保险",
        "装饰",
        "农场",
        "假日",
        "园艺",
        "代理",
        "练字",
        "书法",
        "书画",
        "器材",
        "烘培",
        "焊业",
        "歌城",
        "美容",
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
        "宏源电子",
        "鞋业",
        "鞋厂",
        "叮咚",
        "卓杭",
        "商场",
        "商行",
        "经营部",
        "策马科技",
        "任拓",
    ]
    return all(item not in company_text for item in company_blacks)


Query = [
    "Java",
    "Java软件开发",
    "软件测试",
    "软件自动化测试",
    "软件功能测试",
    "软件实施",
    "全栈工程师",
    "Python软件测试",
    "软件测试开发",
    "软件性能测试",
]

for item in Query:
    search(URL1 + item + URL2)
driver.quit()
