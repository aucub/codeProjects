import tinydb
import sqlite3

# 创建TinyDB实例并加载JSON数据
db = tinydb.TinyDB("rsinfo.json")
data = db.all()

# 创建SQLite数据库连接
conn = sqlite3.connect("rsinfo.db")
cursor = conn.cursor()

# 创建数据库表
cursor.execute(
    """CREATE TABLE IF NOT EXISTS rsinfo
(id TEXT PRIMARY KEY, url TEXT,  name TEXT,  city TEXT,  address TEXT,  guide TEXT,  scale TEXT,  update_date TEXT,  salary TEXT,  experience TEXT,  degree TEXT,  company TEXT,  industry TEXT,  fund TEXT,  res TEXT,  boss TEXT,  boss_title TEXT,  active TEXT,  description TEXT,  communicate TEXT,  datetime TEXT)"""
)

# 遍历TinyDB中的数据并插入到数据库表
for item in data:
    # 提取JSON对象中的属性值
    url = item.get("url").split("html")[0] + "html"
    id = item.get("id")
    name = item.get("name")
    city = item.get("city")
    address = item.get("address")
    if len(item.get("guide")) > 2:
        guide = item.get("guide")[2:]
    else:
        guide = item.get("guide")
    if "人" not in item.get("scale"):
        scale = ""
    else:
        scale = item.get("scale")
    if len(item.get("update")) > 4:
        update_date = item.get("update")[4:]
    else:
        update_date = item.get("update")
    salary = item.get("salary")
    experience = item.get("experience")
    degree = item.get("degree")
    company = item.get("company")
    industry = item.get("companyTag")
    if len(item.get("fund").splitlines()) > 1:
        fund = item.get("fund").splitlines()[-1]
    else:
        fund = item.get("fund")
    if len(item.get("res").splitlines()) > 1:
        res = item.get("res").splitlines()[-1]
    else:
        res = item.get("res")
    boss = item.get("boss")
    boss_title = item.get("bossTitle")
    active = item.get("active")
    description = item.get("description")
    if "继续沟通" in item.get("communicate"):
        communicate = "继续沟通"
    if "立即沟通" in item.get("communicate"):
        communicate = "立即沟通"
    datetime = item.get("datetime")
    # 插入数据到数据库表
    cursor.execute(
        "INSERT INTO rsinfo (url, id, name, city, address, guide, scale, update_date, salary, experience, degree,     company, industry, fund, res, boss, boss_title, active, description, communicate, datetime) VALUES     (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            url,
            id,
            name,
            city,
            address,
            guide,
            scale,
            update_date,
            salary,
            experience,
            degree,
            company,
            industry,
            fund,
            res,
            boss,
            boss_title,
            active,
            description,
            communicate,
            datetime,
        ),
    )

# 提交更改并关闭连接
conn.commit()
conn.close()
