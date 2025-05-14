#!/usr/bin/env python
# coding: utf-8
import tkinter as tk
from tkinter.constants import CENTER
import subprocess
import sys
import threading
import os

def report():
    
    subprocess.run(['python','D:\\test\\record_CW_0418.py'])
    #subprocess.run(['start', 'D:/report'])
    subprocess.run(['C:/Users/HP/Desktop/test.bat'])
def delete():
    subprocess.run(['C:/Users/HP/Desktop/delete_file_sqlite.bat'])


def run():
    #subprocess.run("C:\\Users\\User\\Desktop\\test.bat")
    threading.Thread(target=test).start()
def test():
    global p
    print('程式開始')
    p = subprocess.Popen("C:\\Users\\HP\\Desktop\\ocr_onefile.bat", stdout=subprocess.PIPE, bufsize=1, text=True)
    while p.poll() is None:
        msg = p.stdout.readline().strip() # read a line from the process output
        if msg:
            print(msg)
def terminate():
    subprocess.Popen.terminate(p)
    print('程式停止')    

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
win.title('AI效期辨識')
win.geometry('900x1000')
win.resizable(True, True)
#win.iconbitmap('D:\\OCR\\itri.ico')
win.configure(background='lavender')

#Button
b1 = tk.Button(text = '執行影像辨識程式', font = ('Microsoft JhengHei',20,'bold'), 
               padx = 5, pady = 5, bg='linen', command=run,
               activeforeground='DodgerBlue3')
b1.grid(column = 0, row = 0)#place(x=300, y=150, anchor=CENTER)

b2 = tk.Button(win, text="停止影像辨識程式", font = ('Microsoft JhengHei',20,'bold'), 
               padx = 5, pady = 5, bg = 'linen',command=terminate,#win.destroy,
               activeforeground='tomato')
b2.grid(column = 0, row = 1)#place(x=300, y=250, anchor=CENTER)

b3 = tk.Button(text = '生成報表', font = ('Microsoft JhengHei',20,'bold'), 
               padx = 5, pady = 5, bg='linen', command=report,
               activeforeground='dark olive green')
b3.grid(column = 1, row = 0)

b4 = tk.Button(text = '刪除所有檔案', font = ('Microsoft JhengHei',20,'bold'), 
               padx = 5, pady = 5, bg='linen', command=delete,
               activeforeground='dark olive green')
b4.grid(column = 1, row = 1)

b5 = tk.Button(text = '關閉此視窗', font = ('Microsoft JhengHei',20,'bold'), 
               padx = 5, pady = 5, bg='linen', command=win.destroy,
               activeforeground='dark olive green')
b5.grid(column = 2, row = 0, rowspan=2)

frame = tk.Frame(win)
frame.grid(column = 0, row = 2, columnspan=3, sticky='NSWE') #'expand=True, fill='both'

text = tk.Text(frame, font = (10), width=100, height=50)
text.pack(side='left', fill='both', expand=True)

scrollbar = tk.Scrollbar(frame)
scrollbar.pack(side='right', fill = 'y')

text['yscrollcommand'] = scrollbar.set
scrollbar['command'] = text.yview

old_stdout = sys.stdout    
sys.stdout = Redirect(text)

win.after_idle(run)

win.mainloop()
sys.stdout = old_stdout