import sqlite3
import mysql.connector
from datetime import datetime

# 连接SQLite数据库
sqlite_conn = sqlite3.connect("rsinfo.db")
sqlite_cursor = sqlite_conn.cursor()

# 查询SQLite数据库中所有的数据
sqlite_cursor.execute("SELECT * FROM rsinfo")
rows = sqlite_cursor.fetchall()

# 连接MySQL数据库配置
mysql_config = {
    "user": "wSiWRdz4LwrdWfR.root",
    "password": "npL8MMbArl6jWNt9",
    "host": "gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
    "database": "rsinfo",
    "raise_on_warnings": True,
    "port": 4000,
}

# 连接MySQL数据库
mysql_conn = mysql.connector.connect(**mysql_config)
mysql_cursor = mysql_conn.cursor()

# 准备插入命令
insert_stmt = (
    "INSERT INTO RsInfo (id, url, name, city, address, guide, scale, update_date, "
    "salary, experience, degree, company, industry, fund, res, boss, boss_title, "
    "active, description, communicated, checked_date) "
    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
)
i = 0

for row in rows:
    i += 1
    (
        id,
        url,
        name,
        city,
        address,
        guide,
        scale,
        update_date_str,
        salary,
        experience,
        degree,
        company,
        industry,
        fund,
        res_str,
        boss,
        boss_title,
        active,
        description,
        communicate_str,
        datetime_str,
    ) = row
    # 将字符串日期转换为日期对象
    update_date = (
        datetime.strptime(update_date_str, "%Y-%m-%d").date()
        if update_date_str
        else None
    )
    res = datetime.strptime(res_str, "%Y-%m-%d").date() if res_str else None
    checked_date = (
        datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S") if datetime_str else None
    )

    # 将字符串 “立即” 转换为布尔值
    communicated = 0 if "立即" in communicate_str else 1

    # 执行 MySQL 插入语句
    try:
        mysql_cursor.execute(
            insert_stmt,
            (
                id,
                url,
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
                communicated,
                checked_date,
            ),
        )
        if i % 1000 == 0:
            print("inserted {} rows".format(i))
            mysql_conn.commit()
    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))
        # Handle errors if necessary

# 关闭数据库连接
# 提交更改

sqlite_conn.close()
mysql_cursor.close()
mysql_conn.close()

print("Data transfer complete.")
