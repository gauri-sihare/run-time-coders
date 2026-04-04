import sqlite3
import matplotlib.pyplot as plt

conn = sqlite3.connect("posture.db")
cursor = conn.cursor()

cursor.execute("SELECT date, good_time, bad_time FROM records")
data = cursor.fetchall()

dates = []
good = []
bad = []

for row in data:
    dates.append(row[0])
    
    # convert "10m 20s" → minutes
    g = int(row[1].split("m")[0])
    b = int(row[2].split("m")[0])

    good.append(g)
    bad.append(b)

plt.plot(dates, good, label="Good Time", marker='o')
plt.plot(dates, bad, label="Bad Time", marker='o')

plt.xlabel("Date")
plt.ylabel("Minutes")
plt.title("Posture Report")
plt.legend()
plt.xticks(rotation=30)

plt.show()