from ast import List
import os
from attr import dataclass
import attr
import requests
import toml


@dataclass
@attr.s(init=False)
class Config:
    cookies_name: str = ""
    query_cookies: bool = False
    user_data_dir: str = ""
    captcha_image_path: str = "captcha"
    download_captcha: bool = True
    captcha_distinguish_type: int = 1
    timeout: int = 25
    sleep: float = 0.1
    sleep_long: float = 6.0
    max_retries: int = 3
    chat: bool = False
    skip_known: bool = False
    graduate: int = 23
    salary_max: int = 10  # 最大薪水
    active_block_list: List = [
        "半年",
        "月内",
        "本月",
        "周内",
        "本周",
        "7日",
    ]  # 活跃时间阻止名单
    offline_list: List = [
        "不支持在线",
        "不支持线上",
        "线下面试",
        "线下笔试",
        "现场面试",
        "现场机考",
        "不接受线上",
        "未开放线上",
        "现场coding",
        "附近优先",
    ]
    scale_block_list: List = ["-20"]  # 规模阻止名单
    degree_block_list: List = ["硕", "博"]  # 学历阻止名单
    experience_block_list: List = []  # 经验阻止名单
    city_block_list: List = []  # 城市阻止名单
    boss_title_block_list: List = []  # boss职位阻止名单
    industry_block_list: List = []  # 行业阻止名单
    name_block_list: List = []  # 名称阻止名单
    company_block_list: List = []  # 公司阻止名单
    fund_min: float = 29.0  # 最小注册资金
    res: int = 31536000  # 最晚成立时间
    guide_block_list: List = []  # 导航阻止名单
    update: int = 2592000  # 最旧更新时间
    offline_interview: bool = True  # 线下检查
    offline_city_list: List = []  # 线下城市
    description_min: int = 35  # 最短描述
    description_keyword_list: List = []  # 描述必备词
    description_block_list: List = []  # 描述阻止名单
    description_experience_block_list: List = []  # 描述经验阻止名单
    query_list: List = []
    query_city_list: List = ["100010000"]
    query_param: str = "&experience=101,102,103,104&scale=302,303,304,305,306&degree=209,208,206,202,203"
    salary_list: List = ["404", "403"]
    page_min: int = 1
    page_max: int = 6


def load_config() -> Config:
    if os.getenv("CONFIG_URL"):
        env_config_url = str(os.getenv("CONFIG_URL"))
        response = requests.get(env_config_url)
        response.raise_for_status()
        print(f"load config from {env_config_url}")
        with open("config.toml", "wb") as file:
            file.write(response.content)
    with open("config.toml", "r") as f:
        config_dict = toml.load(f)
    return Config(**config_dict)


def save_config(config: Config) -> None:
    with open("config.toml", "w") as f:
        toml.dump(attr.asdict(config), f)


if __name__ == "__main__":
    config = Config()
    save_config(config)
