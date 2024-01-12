import sqlite3

conn = sqlite3.connect("../rsinfo.db")

cursor = conn.cursor()

with open("rsinfo.sql", "r") as file:
    script = file.read()
    cursor.executescript(script)

conn.commit()

conn.close()
