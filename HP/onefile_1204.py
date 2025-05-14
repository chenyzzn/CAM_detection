from ultralytics import YOLO 
from paddleocr import PaddleOCR
import cv2
import re
import pandas as pd 
import time
import numpy as np
import os
import datetime
import sqlite3
import glob
from shutil import rmtree
import dateform
from save_write import *
from PIL import ImageFont, ImageDraw, Image 

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

print("Importing Models.....")
model = YOLO("C:\\AI_exp\\model\\yolo_0215.pt")
ocr = PaddleOCR(rec_model_dir="C:\\AI_exp\\model\\CW_new_0510" , det_model_dir="C:\\AI_exp\\model\\oscar_det",
                use_angle_cls=True, lang='en', use_gpu=False)

i = 0
img_rate=0.6
img_show_rate=0.4
print("Successfully Imported Models")

print("Collecting Data.....")
dfitno = pd.read_excel("C:\\AI_exp\\HP\\Partdata\\itfpara_POC.xlsx")
dfdate = pd.read_excel("C:\\AI_exp\\HP\\Partdata\\px_main.xlsx")
#dfdate['ITF'] = dfdate['ITF'].apply(lambda x : '{:0>14}'.format(x))
dfdate['貨號'] = dfdate['貨號'].apply(lambda x : '{:0>8}'.format(x))
dfdate = dfdate.set_index("ITF")

print("Successfully Collected Data")


def cut_box(img0):
    #從圖案中心裁切=====================================================  
    img=img0
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #轉為灰階圖
    ret, img = cv2.threshold(img, 80, 255, cv2.THRESH_BINARY) #二值化：如果大於 88 就等於 255，反之等於 0
    contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) #取出二值圖的輪廓
    areas = [cv2.contourArea(c) for c in contours]#1
    max_index = areas.index(max(areas))#2
    max_rect =cv2.minAreaRect(contours[max_index])#3
    max_box = cv2.boxPoints(max_rect)#4
    #max_box = np.int0(max_box)#5
    x, y, h, w =cv2.boundingRect(max_box) #取得包覆指定輪廓點的最小正矩形 #b = event.key[1].split("_") #分割符號為 "-"
    if x>=0 and y>=0 : img0 = img0[y:y+w, x: x+h] #裁切所需要的範圍 #imgy=img0.shape[0]      #imgx=img0.shape[1]   #if imgy > imgx  : 
    return img0
        
 
def trans_square(img):
    #图片转正方形边缘使用0填充
    img_h, img_w, img_c = img.shape
    if img_h != img_w:
        long_side = max(img_w, img_h)
        short_side = min(img_w, img_h)
        loc = abs(img_w - img_h) // 2
        img = img.transpose((1, 0, 2)) if img_w < img_h else img  # 如果高是长边则换轴，最后再换回来
        background = np.zeros((long_side, long_side, img_c), dtype=np.uint8)  # 创建正方形背景
        background[loc: loc + short_side] = img[...]  # 数据填充在中间位置
        img = background.transpose((1, 0, 2)) if img_w < img_h else background
    return img


def yolo(img0):
    results1 = model.predict(img0, max_det = 1,conf = 0.3,
                             iou = 0.1 , line_width=1) #設定顯卡序號, device = 0
    boxs = results1[0].boxes.xyxy
    for result in results1:
        for c in result.boxes.cls:
            cl = str(int(c))
    #yolo_conf=result.boxes.conf[0]

    box=boxs[0] 
    x1 = int(box[0]-8)
    y1 = int(box[1]-5)
    x2 = int(box[2]+20)
    y2 = int(box[3]+6)
    
    #轉灰階、旋轉、分割製造日期(class2-5)
    if cl == '0': #一般圖片
        img_lab=cv2.cvtColor(img0[y1:y2,x1:x2].copy(), cv2.COLOR_RGB2GRAY)
    elif cl == '1': #反向圖片
        img_lab=cv2.cvtColor(img0[y1:y2,x1:x2].copy(), cv2.COLOR_RGB2GRAY)
        img_lab = cv2.rotate(img_lab, cv2.ROTATE_180)
    elif cl == '2': #延伸型
        y2 = y2 - int(abs(y2 - y1)/2)
        img_lab=cv2.cvtColor(img0[y1:y2,x1:x2].copy(), cv2.COLOR_RGB2GRAY)
    elif cl == '3': #延伸+反向
        y2 = y2 - int(abs(y2 - y1)/2)
        img_lab=cv2.cvtColor(img0[y1:y2,x1:x2].copy(), cv2.COLOR_RGB2GRAY)
        img_lab = cv2.rotate(img_lab, cv2.ROTATE_180)
    elif cl == '4': #疊加
        x1 = x1 + int(abs(x2-x1)/2)
        img_lab=cv2.cvtColor(img0[y1:y2,x1:x2].copy(), cv2.COLOR_RGB2GRAY)
    elif cl == '5': #疊加+反向
        x1 = x1 + int(abs(x2-x1)/2)
        img_lab=cv2.cvtColor(img0[y1:y2,x1:x2].copy(), cv2.COLOR_RGB2GRAY)
        img_lab = cv2.rotate(img_lab, cv2.ROTATE_180)
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (4, 6))
    img_Kernal = cv2.erode(img_lab, kernel)

    return img_Kernal, x1, x2, y1, y2, cl

def text(t_img, text, position, font_path, font_size, color):
    img_pil = Image.fromarray(cv2.cvtColor(t_img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    font = ImageFont.truetype(font_path, font_size)
    draw.text(position, text, font=font, fill=color)
    t_img[:] = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    return t_img

def on_ocr(folder:str) -> None:
    while True:
        filepath = glob.glob(folder)
        time.sleep(0.3) 
        for filepath in filepath:    
            start = time.time()
            current = datetime.datetime(2024, 5, 11, 10, 20, 30).strftime("%Y-%m-%d %H:%M:%S")
            global i
            img0 = 0
            filename = filepath[14:]
            try:
                img_flow = cv2.imread(filepath) #讀取圖片
                i+= 1
            except: 
                print('讀取錯誤')
            
            if "NOREAD" in filename: #NoReadBox
                try:
                    os.remove(filepath)
                    #write_other(filename, 'NOREAD')
                    write_RCAM(filename, 'NA', 'NOREAD', 'NA')
                    print('NOREAD')
                
                    img0 = 0
                    continue
                except:continue
                
            elif "_1_" in filename: #併箱
                try:
                    os.remove(filepath)
                    #write_other(filename, 'SBS')
                    write_RCAM(filename, 'NA', 'SBS', 'NA')
                    print('併箱')
                    
                    img0 = 0
                    continue
                except:continue
            elif len(filename)>=55: #flow box
                try:
                    os.remove(filepath)
                    #write_other(filename, 'FLOWBOX')
                    write_RCAM(filename, 'NA', 'FL', 'NA')
                    print('物流箱')
                    
                    img0 = 0
                    continue
                except: continue
            elif filename.endswith(".jpg") and len(filename) == 54: #正常照片
                try: #預處理
                    img0 = cut_box(img_flow) #切箱
                    img0 = cv2.rotate(img0, cv2.ROTATE_90_CLOCKWISE) #轉90度
                    img0 = trans_square(img0) #轉成正方形並填充
                    img0 = cv2.resize(img0, (3840,3840)) #設定圖片大小3840x3840
                    cv2.putText(img0, current, (2800, 100), cv2.FONT_HERSHEY_COMPLEX_SMALL, 4, (255, 0, 0), 4, cv2.LINE_AA) 
                except: #無法預處理則存到ERROR
                    itemname = filename[34:48]
                    save_file_error(filename, img_flow)
                    cv2.putText(img_flow, current, (2800, 100), cv2.FONT_HERSHEY_COMPLEX_SMALL, 4, (255, 0, 0), 4, cv2.LINE_AA) 
                    #write_other(filename, 'ERROR')
                    write_RCAM(filename, itemname, 'ERROR', 'NA')
            elif 'TEMP' in filepath: 
                rmtree(filepath)
                continue
            else:continue
            
            if type(img0) == np.ndarray and len(filename)==54:
                #num = filename.find(".jpg")
                itemname = filename[34:48] #取得貨號
                try:
                    #yolo==============================================================
                    img_Kernal, x1, x2, y1, y2, cl = yolo(img0)
                    #paddle============================================================
                    txts_conf=ocr.ocr(img_Kernal, det=False)[0][0]
                    txts=txts_conf[0] #辨識出的文字
                    conf=round(txts_conf[1], 3)#信任度
                    #日期格式判斷=======================================================
                    numbers = dateform.special_date(itemname, txts) #轉換特殊日期格式
                    numbers = re.sub(r'[^0-9]', '', numbers) #過濾出數字
                    yearcheck = ['23', '24', '25', '26', "27", '28', '29']
                    
                    if any(x in numbers for x in yearcheck) and (len(numbers) >=6):
                        expd, expmessge = dateform.date_check(itemname, numbers)
                    else:
                        expd ="EXP_not_idfy"
                        expmessge = 'TXT_NG'

                    if expmessge == "TXT_OK": #日期格式正確
                        expdate = int(dfdate.loc[itemname]["允收天數"])
                        manuf = str(dfdate.loc[itemname]["廠商名稱"])
                        print(manuf)
                        y=int(expd[0:4])
                        m=int(expd[4:6])
                        d=int(expd[6:8])
                        txt_conf = expd +","+ txts + "   " +str(conf)
                        cv2.putText(img0, str(i), (100,100), cv2.FONT_HERSHEY_COMPLEX_SMALL,  4, (0, 200, 100), 4, cv2.LINE_AA)
                        cv2.rectangle(img0,(x1, y1), (x2, y2), (0,255,0) , 2)
                        cv2.putText(img0, "class=" + cl, (x1,y1-90), cv2.FONT_HERSHEY_COMPLEX_SMALL,  3, (0, 0, 255), 3, cv2.LINE_AA) 
                        cv2.putText(img0, txt_conf, (x1,y1-50), cv2.FONT_HERSHEY_COMPLEX_SMALL,  2, (0, 255, 0), 2, cv2.LINE_AA)
                        font_path = "NotoSansTC-Regular.ttf"
                        font_size = 100
                        text(img0, manuf, (2500, 150), font_path, font_size, (0, 255, 0))
                        # datecheck= datetime.date(y,m,d) - datetime.date.today() + datetime.timedelta(days = 1) #相差日數 datetime格式
                        # checkday=int(datecheck.days) #相差日數 整數 
                                                        
                        if  ((dfitno['外箱條碼'] == itemname) & (dfitno['製造/有效'] == 'M')).any(): #框選到的是製造日期 
                            checkday = int(datecheck.days) + int(dfdate.loc[itemname]["保存天數"])
                            if checkday >= 0: #如果判斷為製造日期，效期還是負的，就存到OCR_ERROR 
                                datagood = str("No="+ itemname)#寫上條碼、效期、允收期
                                cv2.putText(img0, datagood ,(400 , 100),cv2.FONT_HERSHEY_COMPLEX_SMALL,4, (255, 0, 255), 4, cv2.LINE_AA)
                                cv2.putText(img0, "Ed=" + str(checkday) + " ,Rd=" + str(expdate) ,(100 , 240),cv2.FONT_HERSHEY_COMPLEX_SMALL,4, (0, 255, 255), 4, cv2.LINE_AA)
                                print("ITF=", itemname , " ,expd==" , checkday, " ,day_ok=" , expdate)
                                dfitno.loc[dfitno['外箱條碼']==itemname, '製造/有效'] = 'M'

                                if checkday >= expdate: #正常商品(分資料夾儲存)
                                    img0 = cv2.resize(img0,None,fx=img_rate ,fy=img_rate,interpolation=cv2.INTER_CUBIC)
                                    #write_EXP(filename, itemname, expd, 'OK')
                                    write_RCAM(filename, itemname, 'EXP_OK', expd)
                                    save_file_exp(filename, img0, itemname)
                            
                                else: #NG商品 打X (分資料夾儲存)
                                    cv2.putText(img0, "X" , (500 , 1100),cv2.FONT_HERSHEY_COMPLEX_SMALL,50, (0, 0, 255), 4, cv2.LINE_AA)
                                    img0 = cv2.resize(img0, None, fx=img_rate ,fy=img_rate,interpolation=cv2.INTER_CUBIC)
                                    #save_ocr(filename, itemname, checkday)
                                    #write_EXP(filename, itemname, expd, 'NG')
                                    write_RCAM(filename, itemname, 'NG', expd)
                                    save_file_ng(filename, img0, itemname)
                            
                            else: #如果判斷為製造日期，效期還是負的，就存到OCR_ERROR
                                print('DATE ERROR')
                                img0 = cv2.resize(img0,None,fx=img_rate ,fy=img_rate,interpolation=cv2.INTER_CUBIC)
                                #write_other(filename, 'ERROR')
                                write_RCAM(filename, itemname, 'ERROR', 'NA')
                                
                        else:     #有效日期
                            datecheck= datetime.date(y,m,d) - datetime.date(2024, 5, 11) + datetime.timedelta(days = 1) #相差日數 datetime格式
                            checkday=int(datecheck.days) #相差日數 整數
                            datagood = str("No="+ itemname)#寫上條碼、效期、允收期
                            cv2.putText(img0, datagood ,(400 , 100),cv2.FONT_HERSHEY_COMPLEX_SMALL,4, (255, 0, 255), 4, cv2.LINE_AA)
                            cv2.putText(img0, "Ed=" + str(datecheck.days) + " ,Rd=" + str(expdate) ,(100 , 240),cv2.FONT_HERSHEY_COMPLEX_SMALL,4, (0, 255, 255), 4, cv2.LINE_AA)
                            print("ITF=", itemname , " ,expd=" , checkday, " ,day_ok=" , expdate)
                            
                            if checkday >= expdate: #正常商品(分資料夾儲存)
                                img0 = cv2.resize(img0,None,fx=img_rate ,fy=img_rate,interpolation=cv2.INTER_CUBIC)
                                #save_ocr(filename, itemname, checkday)
                                #write_EXP(filename, itemname, expd, 'OK')
                                write_RCAM(filename, itemname, 'EXP_OK', expd)
                                save_file_exp(filename, img0, itemname)
                            
                            else: #NG商品 打X (分資料夾儲存)
                                cv2.putText(img0, "X" , (500 , 1100),cv2.FONT_HERSHEY_COMPLEX_SMALL,50, (0, 0, 255), 4, cv2.LINE_AA)
                                img0 = cv2.resize(img0, None, fx=img_rate ,fy=img_rate,interpolation=cv2.INTER_CUBIC)
                                #save_ocr(filename, itemname, checkday)
                                save_file_ng(filename, img0, itemname)
                                #write_EXP(filename, itemname, expd, 'NG')
                                write_RCAM(filename, itemname, 'NG', expd)

                        #jj=jj+1
                        
                    else: #日期格式有誤，存到OCR_ERROR_TXT(分資料夾儲存)
                        print('TXT ERROR')
                        txt_conf = expd +","+ txts + "   " +str(conf)
                        cv2.putText(img0, "error=>"+ txts , (200,50), cv2.FONT_HERSHEY_COMPLEX_SMALL,  2, (0, 200, 100), 2, cv2.LINE_AA)
                        cv2.rectangle(img0,(x1, y1), (x2, y2), (0,255,0) , 2)
                        cv2.putText(img0, txt_conf, (x1,y1-50), cv2.FONT_HERSHEY_COMPLEX_SMALL,  2, (0, 255, 0), 2, cv2.LINE_AA) 
                        img0 = cv2.resize(img0,None,fx=img_rate ,fy=img_rate,interpolation=cv2.INTER_CUBIC)
                        save_file_txt(filename, img0, itemname)
                        #write_other(filename, 'ERROR_TXT')
                        write_RCAM(filename, itemname, 'ERROR_TXT', 'NA')

                    
                except: #y或p辨識過程或日期格式有error，存到OCR_ERROR 
                    #jj=jj+1
                    print("====NO TEXT ERROR====")
                    try:
                        img0 = cv2.resize(img0, None, fx=img_rate, fy=img_rate, interpolation=cv2.INTER_CUBIC)
                        save_file_error(filename, img0) #==========>2. Y或P沒抓到 D:\\OCR_ERROR\\  
                        #write_other(filename, 'ERROR')
                        write_RCAM(filename, itemname, 'ERROR', 'NA')
                    except: pass

                #移除檔案  
                try:
                    #img_flow.close()
                    os.remove(filepath)
                except: print('Error while remove')
                    
            else: #非可辨識圖片
                try:
                    itemname = '99999999999999'
                    os.remove(filepath)
                    print('unknown img type')
                except:pass
            end=time.time()
            totaltime = int((end-start)*1000)
            print("Total Img=" + str(i), 'ITF=', itemname, "Totaltime=" + str(totaltime)+'ms')

if __name__ == '__main__':
    on_ocr('D:\\R_CAM\\test\\*')