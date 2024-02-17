import sqlite3
import attr
from pymongo import MongoClient
from datetime import date, datetime
from rs import Rs

uri = (
    "mongodb+srv://root:root@cluster0.xupyqy9.mongodb.net/?retryWrites=true&w=majority"
)

# 假设你已经有了 SQLite 的 db 连接和 MongoDB 的集合
sqlite_connection = sqlite3.connect("rsinfo.db")
mongodb_client = MongoClient(uri)
mongodb_db = mongodb_client["RsInfo"]
rs_collection = mongodb_db["RsInfo"]

cursor = sqlite_connection.cursor()

sqlite_connection.row_factory = sqlite3.Row
# 迭代 SQLite 中的数据，将它们转换为 Rs 实例并存入 MongoDB
cursor.execute("SELECT * FROM RsInfo")
rows = cursor.fetchall()


i = 0
# ... (the code before this part remains the same)

for row in rows:
    i += 1
    # 对日期进行转换
    update_date_converted = datetime.strptime(row[7], "%Y-%m-%d") if row[7] else None
    res_converted = datetime.strptime(row[14], "%Y-%m-%d") if row[14] else None
    checked_date_converted = (
        datetime.strptime(row[20], "%Y-%m-%d %H:%M:%S") if row[20] else None
    )

    # 创建 Rs 实例
    rs_instance = Rs(
        id=row[0],  # Assuming id is in the first column
        url=row[1],  # Adjust the index based on your RsInfo table structure
        name=row[2],
        city=row[3],
        address=row[4],
        guide=row[5],
        scale=row[6],
        update_date=update_date_converted,
        salary=row[8],
        experience=row[9],
        degree=row[10],
        company=row[11],
        industry=row[12],
        fund=row[13],
        res=res_converted,
        boss=row[15],
        boss_title=row[16],
        active=row[17],
        description=row[18],
        communicated="继续" in row[19],  # Replace 19 with the actual index
        checked_date=checked_date_converted,
    )

    # 将实例转化为字典，并且存储到 MongoDB
    rs_dict = attr.asdict(rs_instance)
    # Ensure datetime objects, not date objects
    if isinstance(rs_dict["update_date"], date) and not isinstance(
        rs_dict["update_date"], datetime
    ):
        rs_dict["update_date"] = datetime.combine(
            rs_dict["update_date"], datetime.min.time()
        )
    if isinstance(rs_dict["res"], date) and not isinstance(rs_dict["res"], datetime):
        rs_dict["res"] = datetime.combine(rs_dict["res"], datetime.min.time())

    rs_collection.insert_one(rs_dict)
    if i % 1000 == 0:
        print(f"{i} records have been processed.")


# 关闭 SQLite 连接
sqlite_connection.close()
