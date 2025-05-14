import shutil
import os
import time
import sqlite3

path = 'E:\\R_CAM\\'

def write_sql(ITF, datetime, serial_no, filename)->None:

    conn = sqlite3.connect('D:\\RCAM_0529.sqlite')
    cur = conn.cursor()
    cur.execute('pragma busy_timeout=10000')
    cur.execute('''CREATE TABLE IF NOT EXISTS R_CAM (ITF TEXT, datetime TEXT, serial_no TEXT, filename TEXT)''')
    cur.execute('''INSERT INTO R_CAM (ITF, datetime, serial_no, filename)
                VALUES (?, ?,?,?)''', (ITF, datetime, serial_no, filename))
    conn.commit()

    conn.close()

while True:
    file = os.listdir(path)
    time.sleep(0.3)
    for filename in file:
        filepath = path+filename
        datetime = filename[:14]
        serial_no = filename[15:25]
        if len(filename)==54:
            ITF = filename[34:48]
        elif len(filename)==56:
            ITF = filename[34:50]
        else: ITF = 'NOREAD'
        write_sql(ITF, datetime, serial_no, filename)
        print(filename)
        shutil.move(filepath, 'D:\\RCAM_0529\\'+filename)
    time.sleep(0.3)
    if len(os.listdir(path)) == 0: time.sleep(2)



    





