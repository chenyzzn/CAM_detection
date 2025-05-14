import sqlite3
import cv2
import os
import datetime

R_CAM = 'D:\\R_CAM\\'
T_CAM = 'F:\\'
L_CAM = 'G:\\'

exp = 'OCR_EXP\\'
error = 'OCR_ERROR\\'
txt = 'OCR_ERROR_TXT\\'
ng = 'OCR_EXP_NG\\'
noread = 'OCR_Noread_box\\'
sbs = 'OCR_SBS\\'
flowbox = 'OCR_flow_box\\'

def save_file_exp(filename:str, img0, itemname:str) -> None:
    '''儲存照片到OCR_EXP'''
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    num = filename.find('Cam')
    cam = filename[num-2:num+3]
    if cam == 'R_Cam':
        path = R_CAM+exp+today
    if cam == 'T_Cam':
        path = T_CAM+exp+today
    if cam == 'L_Cam':
        path = L_CAM+exp+today
    path_dir = path +'\\' + itemname + "\\"
    if not os.path.isdir(path): os.mkdir(path) #如果沒目錄就造一個
    if not os.path.isdir(path_dir): os.mkdir(path_dir) #如果沒目錄就造一個
    cv2.imwrite(path_dir + filename ,img0)
    
def save_file_ng(filename:str, img0, itemname:str) -> None:
    '''儲存照片到OCR_EXP_NG'''
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    num = filename.find('Cam')
    cam = filename[num-2:num+3]
    if cam == 'R_Cam':
        path = R_CAM+ng+today
    if cam == 'T_Cam':
        path = T_CAM+ng+today
    if cam == 'L_Cam':
        path = L_CAM+ng+today
    path_dir = path + '\\' + itemname + "\\"
    if not os.path.isdir(path): os.mkdir(path) #如果沒目錄就造一個
    if not os.path.isdir(path_dir): os.mkdir(path_dir) #如果沒目錄就造一個
    cv2.imwrite(path_dir + filename ,img0)
       
def save_file_error(filename:str, img0) -> None:
    '''儲存照片到OCR_ERROR'''
    num = filename.find('Cam')
    cam = filename[num-2:num+3]
    if cam == 'R_Cam':
        path = R_CAM+error
    if cam == 'T_Cam':
        path = T_CAM+error
    if cam == 'L_Cam':
        path = L_CAM+error
    cv2.imwrite(path + filename ,img0)  
    
def save_file_txt(filename:str, img0, itemname:str) -> None:
    '''儲存照片到OCR_ERROR_TXT'''
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    num = filename.find('Cam')
    cam = filename[num-2:num+3]
    if cam == 'R_Cam':
        path = R_CAM+txt+today
    if cam == 'T_Cam':
        path = T_CAM+txt+today
    if cam == 'L_Cam':
        path = L_CAM+txt+today
    path_dir = path + '\\' + itemname + "\\"
    if not os.path.isdir(path): os.mkdir(path) #如果沒目錄就造一個
    if not os.path.isdir(path_dir): os.mkdir(path_dir) #如果沒目錄就造一個
    cv2.imwrite(path_dir + filename ,img0)

def save_file_noread(filename:str, img0) -> None:
    '''儲存照片到OCR_noread_box'''
    num = filename.find('Cam')
    cam = filename[num-2:num+3]
    if cam == 'R_Cam':
        path = R_CAM+noread
    if cam == 'T_Cam':
        path = T_CAM+noread
    if cam == 'L_Cam':
        path = L_CAM+noread
    cv2.imwrite(path + filename ,img0)  
    
def save_file_sbs(filename:str, img0) -> None:
    '''儲存照片到OCR_sbs'''
    num = filename.find('Cam')
    cam = filename[num-2:num+3]
    if cam == 'R_Cam':
        path = R_CAM+sbs
    if cam == 'T_Cam':
        path = T_CAM+sbs
    if cam == 'L_Cam':
        path = L_CAM+sbs
    cv2.imwrite(path + filename ,img0)  

def save_file_flowbox(filename:str, img0) -> None:
    '''儲存照片到OCR_flowbox'''
    num = filename.find('Cam')
    cam = filename[num-2:num+3]
    if cam == 'R_Cam':
        path = R_CAM+flowbox
    if cam == 'T_Cam':
        path = T_CAM+flowbox
    if cam == 'L_Cam':
        path = L_CAM+flowbox
    cv2.imwrite(path + filename ,img0)  

def save_ocr(filename:str, itemname: str, checkday: int) -> None:
    '''將辨識出來的資訊存到SQLite'''
    try:
        conn = sqlite3.connect('C:\\AI_exp\\HP\\Partdata\\database.db')
        cur = conn.cursor()
        cur.execute('pragma busy_timeout=10000')
        cur.execute('''CREATE TABLE IF NOT EXISTS ocr (filename, itemname, checkday)''')
        cur.execute('''INSERT INTO ocr (filename, itemname, checkday)
                    VALUES (?,?,?)''', (filename, itemname, checkday))
        conn.commit()
    except Exception:
        conn.rollback()
    finally:
        conn.close()

def write_EXP(filename:str, itemname:str, expd:str, status:str) -> None:
    '''將exp, exp_NG資訊寫到SQLITE'''
    try:
        num = filename.find('Cam')
        cam = filename[num-2:num+3] 
        conn = sqlite3.connect('C:\\AI_exp\\HP\\Partdata\\OCR.db')
        cur = conn.cursor()
        cur.execute('pragma busy_timeout=10000')
        cur.execute('''CREATE TABLE IF NOT EXISTS EXP (filename TEXT, ITF TEXT, expd TEXT, CAM TEXT, status TEXT, date TEXT, time TEXT)''')
        cur.execute('''INSERT INTO EXP (filename, ITF, expd, CAM, status, date, time)
                    VALUES (?,?,?,?,?, date(CURRENT_TIMESTAMP, 'localtime'), time(CURRENT_TIMESTAMP, 'localtime'))''', (filename, itemname, expd, cam, status))
        conn.commit()
    except Exception:
        conn.rollback()
    finally:
        conn.close()

def write_other(filename:str, status:str) -> None:
    '''將error, error_txt, noread, sbs, flowbox寫到SQLITE'''
    try: 
        conn = sqlite3.connect('C:\\AI_exp\\HP\\Partdata\\OCR.db')
        cur = conn.cursor()
        cur.execute('pragma busy_timeout=10000')
        cur.execute('''CREATE TABLE IF NOT EXISTS OTHER (filename TEXT, status TEXT, date TEXT, time TEXT)''')
        cur.execute('''INSERT INTO OTHER (filename, status, date, time)
                    VALUES (?,?, date(CURRENT_TIMESTAMP, 'localtime'), time(CURRENT_TIMESTAMP, 'localtime'))''', (filename, status))
        conn.commit()
    except Exception:
        conn.rollback()
    finally:
        conn.close()

def write_RCAM(filename, itemname, status, expd):
    '''寫上RCAM照片資訊'''
    try: 
        conn = sqlite3.connect('C:\\AI_exp\\HP\\Partdata\\OCR2.db')
        cur = conn.cursor()
        cur.execute('pragma busy_timeout=10000')
        cur.execute('''CREATE TABLE IF NOT EXISTS RCAM (filename TEXT, itemname TEXT, status TEXT, expd TEXT, CAM TEXT, date TEXT, time TEXT)''')
        cur.execute('''INSERT INTO RCAM (filename, itemname, status, expd, CAM, date, time)
                    VALUES (?,?,?,?,'R_Cam', date(CURRENT_TIMESTAMP, 'localtime'), time(CURRENT_TIMESTAMP, 'localtime'))''',
                      (filename, itemname, status, expd))
        conn.commit()
    except Exception:
        conn.rollback()
    finally:
        conn.close()  

def write_TCAM(filename, itemname, status, expd):
    '''寫上RCAM照片資訊'''
    try: 
        conn = sqlite3.connect('C:\\AI_exp\\HP\\Partdata\\OCR2.db')
        cur = conn.cursor()
        cur.execute('pragma busy_timeout=10000')
        cur.execute('''CREATE TABLE IF NOT EXISTS TCAM (filename TEXT, itemname TEXT, status TEXT, expd TEXT, CAM TEXT, date TEXT, time TEXT)''')
        cur.execute('''INSERT INTO TCAM (filename, itemname, status, expd, CAM, date, time)
                    VALUES (?,?,?,?,'T_Cam', date(CURRENT_TIMESTAMP, 'localtime'), time(CURRENT_TIMESTAMP, 'localtime'))''',
                      (filename, itemname, status, expd))
        conn.commit()
    except Exception:
        conn.rollback()
    finally:
        conn.close()     
#write_other('20240311132353_0000074257_0_R_Cam_1471010532040011_2.jpg', 'OK')