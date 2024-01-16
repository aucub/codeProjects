from ast import List
from attr import dataclass
import attr
import toml


@dataclass
@attr.s(init=False)
class Config:
    headless: bool = False
    user_data_dir: str = ""
    cookie_path: str = "cookies/cookies.pkl"
    db_path: str = "rsinfo.db"
    stealth: bool = True
    stealth_path: str = "stealth.min.js"
    stealth_url: str = "https://raw.githubusercontent.com/requireCool/stealth.min.js/main/stealth.min.js"
    chrome_location: str = ""
    timeout: int = 15
    sleep: float = 0.9
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
    with open("config.toml", "r") as f:
        config_dict = toml.load(f)
    return Config(**config_dict)


def save_config(config: Config) -> None:
    with open("config.toml", "w") as f:
        toml.dump(attr.asdict(config), f)


if __name__ == "__main__":
    config = Config()
    save_config(config)
