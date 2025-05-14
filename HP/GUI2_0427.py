#!/usr/bin/env python
# coding: utf-8
import tkinter as tk
from tkinter.constants import CENTER
import subprocess
#import sys
import threading
import os
import sqlite3
import datetime
import smtplib
from email.mime.text import MIMEText
from tkinter import ttk
from tkinter import messagebox as msgbox


GMT = datetime.timezone(datetime.timedelta(hours=8))
now = datetime.datetime.now(tz=GMT)
year = now.year
month = now.month
day = now.day


#函數================================================================================
def create_query(CAM:str, type:str) -> str:
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    if type == 'total':
        query = f'''SELECT count(*) FROM {CAM} WHERE date = '{today}';'''
    elif type == 'NG':
        query = f'''SELECT COUNT(*) FROM {CAM} WHERE date = '{today}' AND status = 'NG';'''
    return query
    

def query(CAM, type) -> int:
    '''查詢照片數量'''
    try: 
        query = create_query(CAM, type)
        conn = sqlite3.connect('D:\\Partdata\\OCR2.db')
        cur = conn.cursor()
        cur.execute('pragma busy_timeout=10000')
        
        res = cur.execute(query).fetchall()[0][0]
        conn.commit()
        conn.close()
    except:
        res = 0
    return res


def report():
    subprocess.run(['D:/test/report.bat'])
    #subprocess.run(['start', 'D:/report'])
    subprocess.run(['D:/test/open_report.bat'])

def delete():
    subprocess.run(['D:/test/delete_file_sqlite.bat'])


def run():
    global p
    p = subprocess.run("D:\\test\\ocr_onefile.bat")
    #threading.Thread(target=test).start()
def test():
    global p
    print('程式開始')
    p = subprocess.Popen("D:\\test\\ocr_onefile.bat", stdout=subprocess.PIPE, bufsize=1, text=True)
    while p.poll() is None:
        msg = p.stdout.readline().strip() # read a line from the process output
        if msg:
            print(msg)
def terminate():
    subprocess.run("D:\\test\\close.bat")
    #subprocess.Popen.terminate(p)
    print('程式停止')    

def close():
    subprocess.run('D:\\test\\close_all.bat')

def start_running_task(task, msg):
    def check_thread():   # 檢查執行緒
        if thread.is_alive():   # 執行緒還沒結束 : 繼續每 100 ms 檢查一次
            progress_win.after(100, check_thread) # 每 100 ms 檢查執行緒 
        else:  # 若執行緒已結束關閉進度條視窗            
            progress_win.destroy()
            msgbox.showinfo('通知訊息', '報表已製作完成')
    # 建立 TopLevel 彈出視窗
    progress_win=tk.Toplevel(win)  
    progress_win.title('處理進度')
    progress_win.update_idletasks()  # 強制更新視窗更新, 處理所有事件
    progress_win.geometry('400x140')  # 將彈出視窗左上角拉到指定座標並設定大小
    progressbar=ttk.Progressbar(progress_win, mode='indeterminate', length=250)
    progressbar.pack(padx=3, pady=30)
    progressbar.start(10)   # 起始進度條並設定速度 (值越小跑越快)
    label=ttk.Label(progress_win)  # 顯示提示詞用
    label.config(text=msg, font=('Helvetica', 10, 'bold'))  # 設定字型大小
    label.pack(padx=3, pady=3)    
    thread=threading.Thread(target=task)  # 建立執行緒
    thread.start()    # 啟始執行緒
    progress_win.after(100, check_thread)  # 每 100 ms 檢查執行緒是否還存活

class Redirect():

    def __init__(self, widget, autoscroll=True):
        self.widget = widget
        self.autoscroll = autoscroll

    def write(self, text):
        self.widget.insert('end', text)
        if self.autoscroll:
            self.widget.see('end')

#視窗============================================================
win = tk.Tk()
win.title('AI效期辨識240505v1')
win.geometry('900x700')
win.resizable(True, True)
#win.iconbitmap('D:\\OCR\\itri.ico')
win.configure(background='lavender')

#變數
a1 = tk.StringVar()
a2 = tk.StringVar()
a3 = tk.StringVar()
a4 = tk.StringVar()
a5 = tk.StringVar()
a6 = tk.StringVar()


def showTime(): #目前時間
    now = datetime.datetime.now(tz=GMT).strftime('%H:%M:%S')   # 取得目前的時間，格式使用 H:M:S
    a5.set(now)                    # 設定變數內容
    win.after(1000, showTime)    # 視窗每隔 1000 毫秒再次執行一次 showTime()

def showtimedelta(): #從6:00到現在的時間差
    timedelta = datetime.datetime.now(tz=GMT) - datetime.datetime(year, month, day, 6,0,0,tzinfo=GMT)  # 取得目前的時間，格式使用 H:M:S
    timedelta = str(timedelta - datetime.timedelta(microseconds=timedelta.microseconds))
    a6.set(timedelta)                    # 設定變數內容
    win.after(1000, showtimedelta)    # 視窗每隔 1000 毫秒再次執行一次 showTime()

def rImgNum():
    num = query('RCAM', 'total')   
    a1.set(num)  
    win.after(10000, rImgNum)    # 視窗每隔 10000 毫秒再次執行一次

def tImgNum():
    num = query('TCAM', 'total')   
    a2.set(num)  
    win.after(10000, tImgNum)    # 視窗每隔 10000 毫秒再次執行一次

def rNGNum():
    num = query('RCAM', 'NG')   
    a3.set(num)  
    win.after(10000, rNGNum)    # 視窗每隔 10000 毫秒再次執行一次

def tNGNum():
    num = query('TCAM', 'NG')   
    a4.set(num)  
    win.after(10000, tNGNum)    # 視窗每隔 10000 毫秒再次執行一次

def send_email(message:str) -> None:
    msg = MIMEText(message, 'plain', 'utf-8') # 郵件內文
    msg['Subject'] = 'test測試'            # 郵件標題
    msg['From'] = 'carolyn'                  # 暱稱或是 email
    msg['To'] = '19991206abcd@gmail.com'   # 收件人 email
    #msg['Cc'] = 'oxxo.studio@gmail.com, XXX@gmail.com'   # 副本收件人 email ( 開頭的 C 大寫 )
    #msg['Bcc'] = 'oxxo.studio@gmail.com, XXX@gmail.com'  # 密件副本收件人 email

    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.ehlo()
    smtp.starttls()
    smtp.login('19991206abcd@gmail.com','wgclyfzruhssvbnp')
    status = smtp.send_message(msg)
    smtp.quit()

def alert():
    num1 = os.listdir('D:\\R_CAM\\')
    num2 = os.listdir('E:\\T_CAM\\') 
    message = ''
    if len(num1) >1000:
        message = 'R_CAM照片累積超過1000張\n'
    if len(num2) > 1000:
        message = message+'T_CAM照片累積超過1000張\n'
    if message == '':pass
    else: send_email(message)

    win.after(300000, alert) #每隔5分鐘執行一次

#LabelFrame
frame = tk.LabelFrame(win, text = '主要功能', font=('Microsoft JhengHei',13, 'bold'), padx=10, pady=10)
frame.pack(padx=10, pady=10)


#LabelFrame
lbf = tk.LabelFrame(win, text='今日影像辨識資訊', font=('Microsoft JhengHei',13, 'bold'), padx=10, pady=10)
lbf.pack(padx=10, pady=10)

# f2 = tk.LabelFrame(win, text='訊息', font=('Microsoft JhengHei',13, 'bold'), padx=10, pady=10)
# f2.pack(padx=10, pady=10)

#Button
b1 = tk.Button(frame, text = '執行影像辨識程式', font = ('Microsoft JhengHei',20,'bold'), 
               padx = 5, pady = 5, bg='linen', command=run,
               activeforeground='DodgerBlue3')
b1.grid(column = 0, row = 0, padx=10, pady=10)#place(x=300, y=150, anchor=CENTER)

b2 = tk.Button(frame, text="停止影像辨識程式", font = ('Microsoft JhengHei',20,'bold'), 
               padx = 5, pady = 5, bg = 'linen',command=terminate,#win.destroy,
               activeforeground='tomato')
b2.grid(column = 0, row = 1, padx=10, pady=10)#place(x=300, y=250, anchor=CENTER)

b3 = tk.Button(frame, text = '生成報表', font = ('Microsoft JhengHei',20,'bold'), 
               padx = 5, pady = 5, bg='linen', command=lambda: \
                        start_running_task(report, '報表製作中請稍候...'),
               activeforeground='dark olive green')
b3.grid(column = 1, row = 0, padx=10, pady=10)

b4 = tk.Button(frame, text = '刪除所有檔案', font = ('Microsoft JhengHei',20,'bold'), 
               padx = 5, pady = 5, bg='linen', command=delete,
               activeforeground='dark olive green')
#b4.grid(column = 1, row = 1)

b5 = tk.Button(frame, text = '關閉此視窗', font = ('Microsoft JhengHei',20,'bold'), 
               padx = 5, pady = 5, bg='linen', command=close,
               activeforeground='dark olive green')
b5.grid(column = 1, row = 1, padx=10, pady=10)

#Label
tk.Label(lbf, text='目前時間:', font=('Microsoft JhengHei', 15,'bold')).grid(column = 0, row = 5)   # 放入第一個 Label 標籤
tk.Label(lbf, textvariable=a5, font=('Microsoft JhengHei', 15,'bold'), fg = 'SpringGreen4').grid(column = 1, row = 5)   # 放入第二個 Label 標籤，內容是 a 變數

tk.Label(lbf, text='執行時間:', font=('Microsoft JhengHei', 15,'bold')).grid(column = 0, row = 6)   # 放入第一個 Label 標籤
tk.Label(lbf, textvariable=a6, font=('Microsoft JhengHei', 15,'bold'), fg = 'SpringGreen4').grid(column = 1, row = 6)   # 放入第二個 Label 標籤，內容是 a 變數

tk.Label(lbf, text = '======以上數據每10秒更新一次======', font = ('Microsoft JhengHei', 15,'bold')).grid(column = 0, row = 4, columnspan=5)

tk.Label(lbf, text='RCAM辨識總數:', font=('Microsoft JhengHei', 15,'bold')).grid(column = 0, row = 2)   # 放入第一個 Label 標籤
tk.Label(lbf, textvariable=a1, font=('Microsoft JhengHei', 15,'bold'), fg = 'navy').grid(column = 1, row = 2)   # 放入第二個 Label 標籤，內容是 a 變數

tk.Label(lbf, text='TCAM辨識總數:', font=('Microsoft JhengHei', 15,'bold')).grid(column = 2, row = 2)   # 放入第一個 Label 標籤
tk.Label(lbf, textvariable=a2, font=('Microsoft JhengHei', 15,'bold'), fg = 'navy').grid(column = 3, row = 2)   # 放入第二個 Label 標籤，內容是 a 變數

tk.Label(lbf, text='RCAM NG總數:', font=('Microsoft JhengHei', 15,'bold')).grid(column = 0, row = 3)   # 放入第一個 Label 標籤
tk.Label(lbf, textvariable=a3, font=('Microsoft JhengHei', 15,'bold'), fg = 'deep pink').grid(column = 1, row = 3)   # 放入第二個 Label 標籤，內容是 a 變數

tk.Label(lbf, text='TCAM NG總數:', font=('Microsoft JhengHei', 15,'bold')).grid(column = 2, row = 3)   # 放入第一個 Label 標籤
tk.Label(lbf, textvariable=a4, font=('Microsoft JhengHei', 15,'bold'), fg = 'deep pink').grid(column = 3, row = 3)   # 放入第二個 Label 標籤，內容是 a 變數

# title = tk.Label(f2, text='報表製作訊息：', font=('Microsoft JhengHei', 15,'bold'))
# title.grid(column=0, row =0)

# lb = tk.Label(f2, textvariable=msg, font=('Microsoft JhengHei', 15,'bold'))
# lb.grid(column=1, row =0)

showTime()
showtimedelta()
rImgNum()
tImgNum()
rNGNum()
tNGNum()
alert()

#Frame
# frame = tk.Frame(win)
# frame.grid(column = 0, row = 6, columnspan=5, sticky='NSWE') #'expand=True, fill='both'

# text = tk.Text(frame, font = (10), width=100, height=50)
# text.pack(side='left', fill='both', expand=True)

# scrollbar = tk.Scrollbar(frame)
# scrollbar.pack(side='right', fill = 'y')

# text['yscrollcommand'] = scrollbar.set
# scrollbar['command'] = text.yview

#old_stdout = sys.stdout    
#sys.stdout = Redirect(text)

def disable_event():
    pass
win.protocol("WM_DELETE_WINDOW", disable_event) #disable [X]鍵

win.after_idle(run)

win.mainloop()
#sys.stdout = old_stdout