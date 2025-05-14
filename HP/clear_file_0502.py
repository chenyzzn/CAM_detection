import shutil
import os
from os import listdir
from os.path import isfile, join
import sqlite3
import datetime

path = ['E:\\OCR_ERROR\\', 'E:\\OCR_ERROR_TXT\\', 'E:\\OCR_EXP\\', 
        'E:\\OCR_EXP_NG\\', 'E:\\OCR_flow_box\\', 'E:\\OCR_Noread_box',
        'E:\\OCR_SBS', 
        'F:\\OCR_ERROR\\', 'F:\\OCR_ERROR_TXT\\', 'F:\\OCR_EXP\\', 
        'F:\\OCR_EXP_NG\\', 'F:\\OCR_flow_box\\', 'F:\\OCR_Noread_box',
        'F:\\OCR_SBS', 
        'G:\\OCR_ERROR\\', 'G:\\OCR_ERROR_TXT\\', 'G:\\OCR_EXP\\', 
        'G:\\OCR_EXP_NG\\', 'G:\\OCR_flow_box\\', 'G:\\OCR_Noread_box',
        'G:\\OCR_SBS']
#刪除所有檔案(包含子資料夾)
def clear_file():
    for folder in path:
        if not os.path.isdir(folder): pass
        try:
            file = [f for f in listdir(folder)]
            for f in file:
                filepath = folder+str(f)
                if isfile(filepath):  
                    try:
                        os.remove(filepath)
                        print(f'已刪除檔案======={filepath}')
                    except OSError as e:
                        print(f'Error:{e.strerror}')
                elif os.path.isdir(filepath):
                    try:
                        shutil.rmtree(filepath)
                        print(f'已刪除資料夾========{filepath}')
                    except OSError as e:
                        print(f'Error:{e.strerror}')
            print(f'已刪除{folder}中的檔案')
        except:pass
    print('=====已刪除所有檔案=====')

last3day = str(datetime.date.today()-datetime.timedelta(days = 3))
last14day = str(datetime.date.today()-datetime.timedelta(days = 14))

def clear_folder(path):
    folderpath = path+last14day
    try: 
        shutil.rmtree(folderpath)
        print(f'===已刪除資料夾: {folderpath}===')
    except:pass

def clear_table(table):
    try:
        query  = f'DELETE FROM {table} WHERE date <= "{last3day}";'
        conn = sqlite3.connect('D:\\PartData\\OCR2.db', check_same_thread = False)
        cur = conn.cursor()
        cur.execute('pragma busy_timeout=10000')
        cur.execute(query)
        conn.commit()
        print(f'===已刪除SQLite table: {table}===')
    except Exception: 
        conn.rollback()
    finally:
        conn.close()
if __name__ == '__main__':

    clear_table('RCAM')
    clear_table('TCAM')



#input('請按enter鍵關閉視窗:')

    