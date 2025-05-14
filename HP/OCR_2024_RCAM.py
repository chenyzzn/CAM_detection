from paddleocr import PaddleOCR, draw_ocr
from ultralytics import YOLO 
#from paddleocr import paddleocr
#from watchdog.observers import Observer
#from watchdog.events import FileSystemEventHandler
import cv2
import re
import tkinter as tk
import tkinter as ttk
#from PIL import Image, ImageTk, ImageFilter
import pandas as pd 
from PIL import Image, ImageTk, ImageDraw
import time
import numpy as np
import os
import threading
import datetime
import shutil
import sqlite3
#from scipy import ndimage
#import OCR_DATA_OUTOUT
# 載入模型==================================================
#ocr = PaddleOCR(det_model_dir=r"D:\PaddleOCR-release-2.7\output\db_mv3_infer\student",use_angle_cls=True,lang="en",use_gpu=False)
#1920X1920圖放入OCR_1就可以輸出結果
print("模型載入.....")
model = YOLO("C:\\AI_exp\\model\\yolo_0215.pt")
#model = YOLO( "D:\\Dropbox\\0ocr\\OCR_Final\\yolo1920\\runs\\detect\\train89\\weights\\best.pt")
ocr = PaddleOCR(rec_model_dir="C:\\AI_exp\\model\\CW_new_0510" , det_model_dir="C:\\AI_exp\\model\\oscar_det",use_angle_cls=True, lang='en',
                use_gpu=False,
               )#"D:\\model\\ch_PP-OCRv4_rec_infer
file_path_box="C:\\AI_exp\\0511"
output_path="C:\\AI_exp\\OCR_EXP\\"
output_path_yolo_err="C:\\AI_exp\\OCR_ERROR\\"
output_path_txt_err="C:\\AI_exp\\OCR_ERROR_TXT\\"
flow_box_file="C:\\AI_exp\\OCR_flow_box\\"
totaltime=0
img_rate=0.6
img_show_rate=0.4
print("模型載入OK")
print("參數收集.....")
dfitno = pd.read_excel("C:\\AI_exp\\HP\\Partdata\\itfpara_POC.xlsx",index_col="外箱條碼") 
dfdate = pd.read_excel("C:\\AI_exp\\HP\\Partdata\\px_main.xlsx")
#dfdate['ITF'] = dfdate['ITF'].apply(lambda x : '{:0>14d}'.format(x))
dfdate = dfdate.set_index("ITF")
today = datetime.datetime.now().strftime("%Y-%m-%d")
NG_file = open(f'C:\\AI_exp\\HP\\Partdata\\NG_file_RCAM\\NG_file_{today}.txt', 'a')
print("收集OK")

def write_NG(filename:str, itemname:str, expd:str) -> None:
    '''將NG資訊寫到SQLITE'''
    try:
        num = filename.find('Cam')
        cam = filename[num-2:num+3] 
        conn = sqlite3.connect('C:\\AI_exp\\HP電腦備份\\Partdata\\NG.db')
        cur = conn.cursor()
        cur.execute('pragma busy_timeout=10000')
        cur.execute('''CREATE TABLE IF NOT EXISTS NG (filename TEXT, ITF TEXT, expd TEXT, CAM TEXT)''')
        cur.execute('''INSERT INTO NG (filename, ITF, expd, CAM)
                    VALUES (?,?,?,?)''', (filename, itemname, expd, cam))
        conn.commit()
    except Exception:
        conn.rollback()
    finally:
        conn.close()

def on_OCR(): 
    print("新圖片")
    global tk_img
    global path_filename
    global totaltime
    global jj
    mypath=file_path_box
    list1 = os.listdir(mypath)
    for filename in list1:
        IDY="OK"
        #time.sleep(2)
        len_file=len(list1)
        img_lab=np.zeros((10,10),np.uint8)
        img_lab.fill(100)
        img_Kernal=np.zeros((10,10),np.uint8)
        img_Kernal.fill(100)
        #if len_file <=10 : time.sleep(2)
        len_filename=len(filename)
        if len_filename !=54:    #"NOREAD" in filename and len(filename!=50):
            jj=jj+1
            path_filename = mypath+ filename#絕對路 
            img_flow=cv2.imread(path_filename) 
            outputpath=flow_box_file+filename
            try:
                cv2.imwrite(outputpath ,img_flow)#1.物流箱 flow_box_file +filename
                os.remove(path_filename)
            except:
                break    
        else:##讀取圖片
            if filename.endswith(".jpg"):
                idfy="NOK"     #if event.key[1].endswith(".jpg"):#確定試圖像
                #取得貨號  
                path_filename = mypath+ filename#絕對路         
                num = filename.find(".jpg") #長度
                if num ==50 : 
                    itemname = filename[num-16:num-2]#貨號 
                else:
                    itemname = "9999999999"
                #讀取原圖
                try:
                    img0=cv2.imread(path_filename) 
                    #img0=img_s
                except:
                    pass  
                    print("讀取錯誤")  
                start0=time.time()
                #yolo===============================================0.02============================
                try:
                    results1 = model.predict(img0, max_det = 1,conf = 0.3,iou = 0.1 , line_width=1, device = 0)   # show=True ,device=0 ,載入官方模型classes=[0,1],max_det = 1,
                    boxs = results1[0].boxes.xyxy
                    for result in results1:
                        for c in result.boxes.cls:
                            cl = str(int(c))

                    end0=time.time()
                    start1=time.time()
                    x1=0
                    y1=0
                    x2=1
                    y2=1 
                    #切小圖影像辨識
                    if cl=="0":
                        yolo_conf=result.boxes.conf[0]
                        box=boxs[0] 
                        x1 = int(box[0]-8)
                        y1 = int(box[1]-5)
                        x2 = int(box[2]+20)
                        y2 = int(box[3]+6)
                        img_lab=cv2.cvtColor(img0[y1:y2,x1:x2].copy(), cv2.COLOR_RGB2GRAY)
                        kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (4, 6))
                        img_Kernal = cv2.erode(img_lab, kernel)
                    if cl=="1":    
                        yolo_conf=result.boxes.conf[0]
                        box=boxs[0] 
                        x1 = int(box[0]-8)
                        y1 = int(box[1]-5)
                        x2 = int(box[2]+20)
                        y2 = int(box[3]+6)
                        img_lab=cv2.cvtColor(img0[y1:y2,x1:x2].copy(), cv2.COLOR_RGB2GRAY)
                        img_lab = cv2.rotate(img_lab, cv2.ROTATE_180)
                        kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (4, 6))
                        img_Kernal = cv2.erode(img_lab, kernel)
                    if cl=="2": 
                        yolo_conf=result.boxes.conf[0]
                        box=boxs[0] 
                        x1 = int(box[0]-8)
                        y1 = int(box[1]-5)
                        x2 = int(box[2]+20)
                        y2 = int(box[3]+6)
                        #y1 = y1 + int(abs(y2-y1)/2)  
                        y2 = y2 - int(abs(y2 - y1)/2)
                        img_lab=cv2.cvtColor(img0[y1:y2,x1:x2].copy(), cv2.COLOR_RGB2GRAY) 
                        kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (4, 6))
                        img_Kernal = cv2.erode(img_lab, kernel)
                    if cl=="3":    
                        yolo_conf=result.boxes.conf[0]
                        box=boxs[0] 
                        x1 = int(box[0]-8)
                        y1 = int(box[1]-5)
                        x2 = int(box[2]+20)
                        y2 = int(box[3]+6)
                        y2 = y2 - int(abs(y2-y1)/2)
                        img_lab=cv2.cvtColor(img0[y1:y2,x1:x2].copy(), cv2.COLOR_RGB2GRAY)  
                        img_lab = cv2.rotate(img_lab, cv2.ROTATE_180) 
                        kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (4, 6))
                        img_Kernal = cv2.erode(img_lab, kernel)

                    if cl=="4":    
                        yolo_conf=result.boxes.conf[0]
                        box=boxs[0] 
                        x1 = int(box[0]-8)
                        y1 = int(box[1]-5)
                        x2 = int(box[2]+20)
                        y2 = int(box[3]+6)
                        x1 = x1 + int(abs(x2-x1)/2)
                        img_lab=cv2.cvtColor(img0[y1:y2,x1:x2].copy(), cv2.COLOR_RGB2GRAY)   
                        kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (4, 6))
                        img_Kernal = cv2.erode(img_lab, kernel)
                        
                    if cl=="5":    
                        yolo_conf=result.boxes.conf[0]
                        box=boxs[0] 
                        x1 = int(box[0]-8)
                        y1 = int(box[1]-5)
                        x2 = int(box[2]+20)
                        y2 = int(box[3]+6)
                        x2 = x2 - int(abs(x2-x1)/2)
                        img_lab=cv2.cvtColor(img0[y1:y2,x1:x2].copy(), cv2.COLOR_RGB2GRAY)
                        img_lab = cv2.rotate(img_lab, cv2.ROTATE_180)   
                        kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (4, 6))
                        img_Kernal = cv2.erode(img_lab, kernel)
       
                #paddle影像辨識=====================================================
                    print("02_影像辨識")
                    expdate = int(dfdate.loc[itemname]["允收天數"])
                    txts_conf=ocr.ocr(img_Kernal,det=False)[0][0]
                    txts=txts_conf[0]
                    conf=round(txts_conf[1],3)#信任度
                    numbers = special_date(itemname, txts)
                    numbers = re.sub(r'[^0-9]', '', numbers)#過濾出0~9數字
                    yearcheck = ['23', '24', '25', '26', "27", '28']
                    if any(x in numbers for x in yearcheck) and (len(numbers) >=6):
                        expd, expmessge = date_check(itemname, numbers)#,datetype,expdate)
                #========================================================================    
                        if expmessge == "TXT_OK":
                            #cv2.putText(img0, expd, (tl), cv2.FONT_HERSHEY_COMPLEX_SMALL,  2, (0, 255, 255), 3, cv2.LINE_AA)
                            #cv2.rectangle(img0,tl,br,(0,255,255),3)
                            y=int(expd[0:4])
                            m=int(expd[4:6])
                            d=int(expd[6:8])
                            datecheck= datetime.date(y,m,d) - datetime.date.today()#相差日期
                            checkday=int(datecheck.days)
                            if int(datecheck.days) >= 0:#代表有效日 
                                datagood = str("No="+ itemname)# + " ,exp="+ expd)
                                cv2.putText(img0, datagood ,(400 , 100),cv2.FONT_HERSHEY_COMPLEX_SMALL,4, (255, 0, 255), 4, cv2.LINE_AA)
                                cv2.putText(img0, "Ed=" + str(datecheck.days) + " ,Rd=" + str(expdate) ,(100 , 240),cv2.FONT_HERSHEY_COMPLEX_SMALL,4, (0, 255, 255), 4, cv2.LINE_AA)
                                
                                if checkday <= expdate : #and conf >= 0.91 :
                                    IDY="NG"
                                    cv2.putText(img0, "X" , (500 , 1100),cv2.FONT_HERSHEY_COMPLEX_SMALL,50, (0, 0, 255), 4, cv2.LINE_AA)
                                    
                            else:#如果為負則為製造日期
                                datecheck = int(datecheck.days) + int(dfdate.loc[itemname]["保存天數"]) 
                                if datecheck > 0:
                                    datagood = str("No2="+ itemname) # + " ,exp="+ expd)   #+" ,Ed=" + str(datecheck) + " ,Rd=" + str(expdate))
                                    cv2.putText(img0, datagood , (400 , 100),cv2.FONT_HERSHEY_COMPLEX_SMALL,4, (255, 0, 255),4, cv2.LINE_AA)
                                    cv2.putText(img0, "Ed=" + str(datecheck) + " ,Rd=" + str(expdate) ,(100 , 240),cv2.FONT_HERSHEY_COMPLEX_SMALL,4, (0, 255, 255), 4, cv2.LINE_AA)
                                    print("貨號=", itemname , " ,有效天數==" , datecheck , " ,可收天數=" , expdate)
                                    if datecheck <= int(expdate) :#and conf >=0.9 :
                                        IDY="NG"
                                        cv2.putText(img0, "X" , (500 , 1100),cv2.FONT_HERSHEY_COMPLEX_SMALL,50, (0, 0, 255), 4, cv2.LINE_AA)
                                else:
                                    txt_conf = ","+ "error" 
                                    cv2.rectangle(img0,(x1, y1), (x2, y2), (0,255,0) , 2)
                                    cv2.putText(img0, txt_conf, (x1,y1-50), cv2.FONT_HERSHEY_COMPLEX_SMALL,  2, (0, 255, 0), 2, cv2.LINE_AA)    
                                    jj=jj+1
                                    print("貨號無資料===影像辨識問題---") 
                                    txts=""
                                    try:
                                        cv2.imwrite( output_path_yolo_err + filename  ,img0) #========================================>2. Y都沒抓到 D:\\OCR_ERROR\\   
                                    except:
                                        pass
                    else:
                        expd ="EXP_not_idfy"
                        expmessge = 'TXT_NG'
                    jj=jj+1  #+++++++++++++++++++++++++++++++++++++++++++++++++ 
                    txt_conf = expd +","+ txts + "   " +str(conf)
                    cv2.putText(img0, str(jj), (100,100), cv2.FONT_HERSHEY_COMPLEX_SMALL,  4, (0, 200, 100), 4, cv2.LINE_AA)
                    cv2.rectangle(img0,(x1, y1), (x2, y2), (0,255,0) , 2)
                    cv2.putText(img0, "class=" + cl, (x1,y1-90), cv2.FONT_HERSHEY_COMPLEX_SMALL,  3, (0, 0, 255), 3, cv2.LINE_AA)            #====================================================
                    cv2.putText(img0, txt_conf, (x1,y1-50), cv2.FONT_HERSHEY_COMPLEX_SMALL,  2, (0, 255, 0), 2, cv2.LINE_AA)            #====================================================
                except:
                    txt_conf = ","+ "error" 
                    cv2.rectangle(img0,(x1, y1), (x2, y2), (0,255,0) , 2)
                    cv2.putText(img0, txt_conf, (x1,y1-50), cv2.FONT_HERSHEY_COMPLEX_SMALL,  2, (0, 255, 0), 2, cv2.LINE_AA)    
                    jj=jj+1
                    print("貨號無資料===影像辨識問題---") 
                    txts=""

                    try:
                        cv2.imwrite( output_path_yolo_err + filename  ,img0) #========================================>2. Y都沒抓到 D:\\OCR_ERROR\\
                        #pathE = "E:\\TM\\yo\\" + itemname + "\\"
                        #if not os.path.isdir(pathE):  os.mkdir(pathE)#如果沒目錄就造一個
                        #cv2.imwrite(pathE + filename,img0)    
                    except:
                        pass
                    pass

                if txts!="" and IDY !="NG":#正常貨品存檔                    
                    img0 = cv2.resize(img0,None,fx=img_rate ,fy=img_rate,interpolation=cv2.INTER_CUBIC)
                    path =output_path + itemname + "\\"
                    if not os.path.isdir(path):  os.mkdir(path)#如果沒目錄就造一個
                    #正常辨識=============================================================================================
                    if expmessge=="TXT_OK":
                       cv2.imwrite(path + filename ,img0)#=========================================>3.正常畔讀品項D:\\OCR_EXP\\
                       #pathE ="E:\\TM\\ok\\"+ itemname + "\\"
                       #if not os.path.isdir(pathE):  os.mkdir(pathE)#如果沒目錄就造一個
                       #cv2.imwrite(pathE + filename,img0)    
                    #無法辨識文字========================================================================================
                    else:#TXT_NG  
                        path2 =output_path_txt_err + itemname + "\\"
                        cv2.putText(img0, "error=>"+ txts , (200,50), cv2.FONT_HERSHEY_COMPLEX_SMALL,  2, (0, 200, 100), 2, cv2.LINE_AA)
                        if not os.path.isdir(path2):  os.mkdir(path2)#如果沒目錄就造一個
                        cv2.imwrite(path2 + filename ,img0)#========================================>4.無法讀出字

                        #pathE = output_path_train_image + itemname +"\\"
                        #if not os.path.isdir(pathE):  os.mkdir(pathE)#如果沒目錄就造一個
                        img_s=cv2.imread(path_filename)
                        #try:
                        #    cv2.imwrite(pathE + filename ,img_s)#=========================================>5.訓練用圖片
                        #except:
                        #    break    
                #NG=======================================            
                elif IDY=="NG" :
                    write_NG(filename, itemname, expd)
                    img0 = cv2.resize(img0,None,fx=img_rate ,fy=img_rate,interpolation=cv2.INTER_CUBIC)
                    path ="E:\\OCR_EXP_NG\\"+itemname+'\\'
                    if not os.path.isdir(path):  os.mkdir(path)#如果沒目錄就造一個 
                    txts
                    cv2.imwrite(path +filename ,img0) #============================OCR_EXP_NG維持原檔名
                    #path2 ="D:\\OCR_DATA_NG\\"+itemname+'\\'
                    #if not os.path.isdir(path2):  os.mkdir(path2)#如果沒目錄就造一個 
                    #txts
                    #cv2.imwrite(path2+ expd + filename ,img0) #===============OCR_DATA_NG 檔名有加上效期
                    NG_file.write(filename+'\t'+expd+'\n')    #=========將NG圖片資訊(檔名、效期)寫入文字檔
                    NG_file.flush()
                    
                else :
                    print("無文字")
                    #img0 = cv2.resize(img0,None,fx=img_rate ,fy=img_rate,interpolation=cv2.INTER_CUBIC)
                    #cv2.imwrite(output_path_txt_err + filename +".jpg" ,img0)
                    pass    

                end1=time.time()
                paddletime=int((end1-start1)*1000)
                yolotime=int((end0-start0)*1000)
                totaltime = yolotime + paddletime
                print("張數=" + str(jj) ,",det=" + str(yolotime) +"ms,",",rec=" + str(paddletime) +"ms ,alltime= " + str(totaltime))
                #img0 = cv2.resize(img0,None,fx=img_rate ,fy=img_rate,interpolation=cv2.INTER_CUBIC)    
                #cv2showwindow(img_lab,"labsourse",10,10) #cv2showwindow(img_Kernal,"labKernal",10,200)
                #if img0[0][0][0]!=0:
                #cv2showwindow(img0,"result",600,10)
                #img_Image = Image.fromarray(np.uint8(img0))
        try: 
            img00 = cv2.resize(img0,None,fx=img_show_rate ,fy=img_show_rate,interpolation=cv2.INTER_CUBIC)       
            tk_img0 = Image.fromarray(np.uint8(img00))
            tk_img = ImageTk.PhotoImage(tk_img0)    # 轉換為 tk 圖片物件
            label_right.config(image=tk_img) #換圖片
        except:
            pass
        try:#移除檔案                
            #============================================0212
            os.remove(path_filename)
        except:
            print("沒有此檔案")    
        #cv2.imshow("",img0)
        #cv2.waitKey(100)               
    task()
def open():
    global s
#   ret,frame = captrue.read() #取得相機畫面 cv2.imwrite(img_viode,frame) #儲存圖片
    img_right = ImageTk.PhotoImage(Image.open()) #讀取圖片
    label_right.imgtk=img_right #換圖片
    label_right.config(image=img_right) #換圖片
    s = label_right.after(1, open) #持續執行open方法，1000為1秒    
#日期格式辨別============================================================
def date_check(itemnumber, itemdate ):#, datetype, expdate ):
    #today = datetime.date.today()
    y="error"
    m="error"
    d="error"
    num = itemdate.find("202")
    try:#無資料預設YYMD
        datetype=str(dfitno.loc[itemnumber]["日期格式"])
        if datetype=='nan':  
            datetype="YYMD"
    except:
            datetype="YYMD"   
    special_type = ['YYM', 'MYY', 'CMD', 'CSMSD', 'CSMD', 'DEYY',
                     'YYSMSD', "YSMSD", 'KHI', 'KH', 'YM']
    if   datetype=="YYMD" and len(itemdate) >= 8 and num >= 0:
        years=int(itemdate[num: num + 4])
        if 2022 <= years <= 2029 :
            year_str = itemdate[num+0:num+4]
            year = years
            y = "true"
        else:
            y = "error"           
        try:     
            months = int(itemdate[num+4:num+6])
            if 1 <= months <= 12 :
                month_str = itemdate[num+4:num+6]
                month = months
                m = "true"
            else:
                m = "error"         
            days=int(itemdate[num+6:num+8])
            if 1 <= days <= 31 :
                day_str = itemdate[num+6:num+8]
                day = days
                d = "true"
            else:
                d = "error"
        except:
            print("日期格式錯誤")
#==DMYY==============================================
    elif datetype=="DMYY"and len(itemdate) >= 8:
        years=int(itemdate[4:8])
        if 2022 <= years <= 2029 :
            year_str = itemdate[4:8]
            year = years
            y = "true"
        else:
            y = "error"            
        months = int(itemdate[2:4])
        if 1 <= months <= 12 :
            month_str = itemdate[2:4]
            month = months
            m = "true"
        else:
            m = "error"         
        days=int(itemdate[0:2])
        if 1 <= days <= 31 :
            day_str = itemdate[0:2]
            day = days
            d = "true"
        else:
            d = "error"
#==MDYY==============================================    
    elif datetype=="MDYY"and len(itemdate) >= 8:
        years=int(itemdate[4:8])
        if 2022 <= years <= 2029 :
            year_str = itemdate[4:8]
            year = years
            y = "true"
        else:
            y = "error"                    
        months=int(itemdate[0:2])
        if 1 <= months <= 12 :
            month_str = itemdate[0:2]
            month = months
            m = "true"
        else:
            m = "error"         
        days=int(itemdate[2:4])
        if 1 <= days <= 31 :
            day_str = itemdate[2:4]
            day = days
            d = "true"
        else:
            d = "error"
#==DMY==============================================           
    elif datetype=="DMY"and len(itemdate) >= 6:
        years = int(itemdate[4:6])
        years = 2000 + years
        if 2022 <= years <= 2029 :
            year = years
            y = "true"
        else:
            y = "error"                    
        months = int(itemdate[2:4])
        if 1 <= months <= 12 :
            month_str = itemdate[2:4]
            month = months
            m = "true"
        else:
            m = "error"  
        days=int(itemdate[0:2])
        if 1 <= days <= 31 :
            day_str = itemdate[0:2]
            day = days
            d = "true"
        else:
            d = "error"   
#=YMD=======================================
    elif datetype=="YMD"and len(itemdate) >= 6:
        years = int(itemdate[0:2])
        years = 2000 + years
        if 2022 <= years <= 2029 :
            year = years
            y = "true"
        else:
            y = "error"                    
        months = int(itemdate[2:4])
        if 1 <= months <= 12 :
            month_str = itemdate[2:4]
            month = months
            m = "true"
        else:
            m = "error"  
        days=int(itemdate[4:6])
        if 1 <= days <= 31 :
            day_str = itemdate[4:6]
            day = days
            d = "true"
        else:
            d = "error"    
#==special datetype================================                
    elif datetype in special_type and len(itemdate)>=8:
        years = int(itemdate[0:4])
        if 2022 <= years <= 2029 :
            year = years
            y = "true"
        else:
            y = "error"                    
        months = int(itemdate[4:6])
        if 1 <= months <= 12 :
            month_str = itemdate[4:6]
            month = months
            m = "true"
        else:
            m = "error"  
        days=int(itemdate[6:8])
        if 1 <= days <= 31 :
            day_str = itemdate[6:8]
            day = days
            d = "true"
        else:
            d = "error"      
#===========================================                        
    if  y == "true" and m == "true" and d == "true":
        exp = str(year) + month_str + day_str  
        expmessge = "TXT_OK"
    else:
        exp="EXP_not_idfy"
        expmessge = "TXT_NG"      
    return exp , expmessge       
def special_date(itemnumber, txts):
    datetype = str(dfitno.loc[itemnumber]['日期格式'])
    if datetype=='DEYY' and len(txts)>=8: #30 JAN 2024
        month =['JAN', "FEB", "MAR", "APR", "MAY", "JUN", 
                 "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
        num = ["01", "02", "03", "04", "05", "06", 
                "07", "08", "09", "10", "11", "12"]
        for i in range(len(month)):
            if month[i] in txts:
                txts = txts.replace(month[i], num[i])
                txts = re.sub(r'[^0-9]', '', txts)
        txts = txts[4:8]+txts[2:4]+txts[0:2]
    elif datetype == 'CMD' or datetype =='CSMSD'or datetype =='CSMD' and len(txts)>=5: #113.1.30
        txts = txts[txts.find('11'): ]
        txts_split = re.split('\D+', txts)
        y,m,d = txts_split[0], txts_split[1], txts_split[2]
        year = int(y)+1911
        month = ['0'+m if len(m)==1 else m]
        day = ['0'+d if len(d)==1 else d]
        txts = str(year)+month[0]+day[0]
    elif datetype == 'YYM' or datetype =='MYY' and len(txts)>=5: #2024.01 or 2024 01 or 01.2024 or 01 2024
        txts = re.sub('\D+', '', txts)
        if datetype == 'YYM': #202401
            txts = txts[0:4]+txts[4:6]+'01'
        if datetype == 'MYY': #012024
            txts = txts[2:6]+txts[0:2]+'01'
    elif datetype == 'YYSMSD' or datetype =='YSMSD'  and len(txts)>=6: #2024.1.1 or 24.1.1
        txts = txts[txts.find('2'): ]
        txts_split = re.split('\D+', txts)
        y,m,d = txts_split[0], txts_split[1], txts_split[2]
        year = [int(y)+2000 if datetype=='YSMSD' else int(y)]
        month = ['0'+m if len(m)==1 else m]
        day = ['0'+d if len(d)==1 else d]
        txts = str(year[0])+month[0]+day[0]
    elif datetype == 'YM' and len(txts) >= 3: #24.1 or 24.10
        txts = txts[txts.find('2'): ]
        txts_split = re.split('\D+', txts)
        y,m = txts_split[0], txts_split[1]
        year = int(y)+2000
        month = ['0'+m if len(m)==1 else m]
        txts = str(year)+month[0]+'01'
    elif datetype == 'KHI' and len(txts)>=7: #2024K01H30I 2024年01月30日 or 2024年1月30日 
        txts = txts[txts.find('20'): ]
        txts_split = re.split('\D+', txts)
        y,m,d = txts_split[0], txts_split[1], txts_split[2]
        year = int(y)
        month = ['0'+m if len(m)==1 else m]
        day = ['0'+d if len(d)==1 else d]
        txts = str(year)+month[0]+day[0]
    elif datetype == 'KH' and len(txts)>= 6: #2024K10H 2024年1月 or 2024年10月
        txts = txts[txts.find('20'): ]
        txts_split = re.split('\D+', txts)
        y,m = txts_split[0], txts_split[1]
        year = int(y)
        month = ['0'+m if len(m)==1 else m]
        txts = str(year)+month[0]+'01'
    return txts
def image_skill(img):
    kernel=np.array([[0,-1,0],[-1,5,-1],[0,-1,0]],np.float32)
    dst=cv2.filter2D(img,-1,kernel=kernel)
    return dst
def cv2showwindow(img,name,Lx,Ly)  :
    cv2.namedWindow(name,1)
    cv2.moveWindow(name,Lx,Ly) #cv2.resizeWindow(name,Wx,Wy)
    #if img[0][0]!=0 :
    cv2.imshow(name,img)
    cv2.waitKey(100)
    #cv2.destroyAllwindow(name)
def close_window():
    winshow.destroy()
    os._exit()
    #os._exit()
    
    #observer_ocr.stop()
def task():
    timer=threading.Timer(5,on_OCR)    
    timer.start()
    time.sleep(6)
    timer.cancel()
    print("OCR等待新圖片")
    
if __name__ == '__main__':
    j=1
    K=0
    jj=0
    #observer_ocr = Observer()# 创建观察者对象
    #file_Handler = MyOcrEventHanlder()# 创建事件处理对象
    #observer_ocr.schedule(file_Handler,file_path_box,recursive=False)
    #observer_ocr.start()
#視窗======================================================================
    task()
    winshow=tk.Tk()
    winshow.title('GUI')
    winshow.geometry('1180x1280+0+0')#x y
    #frm = ttk.Frame(winshow)#.pack(padx=100,pady=10)#,width=600, height=500, bg="blue").pack()
    #frm.grid()
    button1=tk.Button(winshow,text="Quit", command=winshow.destroy) #.grid(column=100, row=100)
    tk_img= cv2.imread("D:\\3.jpg") #要改
    tk_img = Image.fromarray(np.uint8(tk_img))
    tk_img = ImageTk.PhotoImage(tk_img)    # 轉換為 tk 圖片物件


    #label = tk.Label(winshow, image=tk_img, width=680, height=680)  # 在 Lable 中放入圖片
    label_right= tk.Label(winshow,height=980,width=1180,bg ='black',fg='blue',image = tk_img) 
    #位置

    button1.grid(row=1,column=0,padx=5, pady=2, sticky="nw")
    label_right.grid(row=1,column=0,padx=5, pady=40, sticky="nw") 
    #label_right.pack()
    winshow.mainloop()
