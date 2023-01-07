import sqlite3

con = sqlite3.connect("CustomsDatabase")
cur = con.cursor()
res = cur.execute("SELECT * FROM tariff_data")

for row in res:
    print(row)
