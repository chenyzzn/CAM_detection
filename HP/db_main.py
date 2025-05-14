from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
from read_xml import convert_xml
import os
import pandas as pd
import sqlite3
import threading


folder1 = 'D:\\partdata\\xml\\'
filelist = os.listdir(folder1)

def read_mainfile() -> None:
    '''將主檔中的允收允出天數讀入SQLite'''
    path = 'D:\\Partdata\\px_main.xlsx'
    df = pd.read_excel(path, dtype = {"ITF":"object", '貨號':'object'})
    df = df[['ITF', '允收天數', '允出天數']]
    df = df.rename(columns = {'允收天數':'rd', '允出天數':'xd'})
    conn = sqlite3.connect('D:\\PartData\\database.db', check_same_thread = False)
    cur = conn.cursor()
    cur.execute('pragma busy_timeout=10000')
    cur.execute('''CREATE TABLE if not EXISTS main (ITF TEXT, rd, xd)''')
    df.to_sql('main', conn, if_exists='append', index=False)
    conn.commit()
    conn.close()
    print('讀進商品主檔')

class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        print(event.event_type, event.src_path)
        path = event.src_path
        time.sleep(2)
        convert_xml(path)

def monitor(folder):
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path = folder)
    observer.start()
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt: 
        observer.stop()
    observer.join()

query = '''
WITH t1(filename, CAM, ti, itf) AS (
SELECT *, SUBSTR(filename, 1, 25), SUBSTR(filename, 35, 14) FROM imglist),

t2(filename, CAM, ti, itf, rn) AS (
SELECT *, row_number() OVER(PARTITION BY ti ORDER BY itf) AS rn
FROM t1),

t3(filename, itf) AS (
SELECT filename, itf
FROM t2
WHERE rn=1
GROUP BY ti),

t4(filename, itf, rn) AS (
SELECT *, row_number() OVER(PARTITION BY itf) AS rn FROM t3),

t5(ITEM_NO, CUSC_CHUTEID, IJP, BARCODE, SYSNO, filename, rn) AS (
SELECT *, row_number() OVER(PARTITION BY BARCODE ORDER BY ITEM_NO) AS rn 
FROM xml),

t6(ITF, rd, xd) AS (
SELECT CAST(PRINTF('%014d', ITF) AS TEXT) AS ITF, rd, xd FROM main)

INSERT INTO check_ocr
SELECT CUSC_CHUTEID, IJP, BARCODE, SYSNO, t4.filename AS filename, rd, xd, checkday,
CASE 
	WHEN length(t5.IJP) = 8 AND t6.xd > ocr.checkday THEN 'NG'
	WHEN length(t5.IJP) = 3 AND t6.rd > ocr.checkday THEN 'NG'
	ELSE 'OK' 
END AS status
FROM t5
JOIN t4 ON (t5.BARCODE = t4.itf AND t5.rn = t4.rn)
JOIN t6 ON (t5.BARCODE = t6.ITF)
JOIN ocr ON (ocr.filename = t4.filename);
'''

def check_expd() -> None:
    '''比對ocr, 主檔, 分撿指示, 照片順序'''
    while True:
        try:
            conn = sqlite3.connect('D:\\PartData\\database.db', check_same_thread = False)
            cur = conn.cursor()
            cur.execute('pragma busy_timeout=10000')
            cur.execute(query)
            conn.commit()
            print('比對完成')
        except Exception: 
            conn.rollback()
            print('資料庫發生錯誤')
        finally:
            conn.close()
        
        time.sleep(1)
        #check_expd()

def main() -> None:
    read_mainfile() #讀進商品主檔
    for file in filelist:
        filepath = folder1+file
        convert_xml(filepath)
    th1 = threading.Thread(target = monitor, args = (folder1, )) #一有新的分撿指示就讀進db
    th2 = threading.Thread(target = check_expd, args = ()) #比對ocr, 主檔, 分撿指示, 照片順序
    
    th1.start()
    th2.start()
    
if __name__ == '__main__':
    main()

