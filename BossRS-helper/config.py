from ast import List
from attr import dataclass
import attr
import toml


@dataclass
@attr.s(init=False)
class Config:
    headless: bool = False
    user_data_dir: str = ""
    cookie_path: str = "cookies.pkl"
    db_path: str = "rsinfo.db"
    timeout: int = 10
    chat: bool = False
    salary_max: int = 10  # 最大薪水
    active_blacks: List = [
        "半年",
        "月内",
        "本月",
        "周内",
        "本周",
        "7日",
    ]  # 活跃时间黑名单
    scale_blacks: List = ["-20"]  # 规模黑名单
    degree_blacks: List = ["硕", "博"]  # 学历黑名单
    experience_blacks: List = []  # 经验黑名单
    city_blacks: List = []  # 城市黑名单
    bossTitle_blacks: List = []  # boss职位黑名单
    industry_blacks: List = []  # 行业黑名单
    name_blacks: List = []  # 标题黑名单
    company_blacks: List = []  # 公司黑名单
    fund_blacks: List = []  # 资金黑名单
    res: int = 31536000  # 最晚成立时间
    guide_blacks: List = []  # 导航黑名单
    update: int = 2592000  # 最旧更新时间
    offline_interview: bool = True  # 线下检查
    offline_citys: List = []  # 线下城市
    description_min: int = 50  # 最短描述
    description_keywords: List = []  # 描述必备词
    description_blacks: List = []  # 描述黑名单
    description_experience_blacks: List = []  # 描述经验黑名单
    querys: List = []
    query_params: str = "&city=100010000&experience=101,102,103,104&scale=302,303,304,305,306&degree=209,208,206,202,203"
    salarys: List = []
    range_min: int = 1
    range_max: int = 15


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
