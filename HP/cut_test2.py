import cv2
import os
import numpy as np
import time
import threading
import datetime
import multiprocessing
import sqlite3

i=0 #總數
j=0 #noread
k=0 #併箱
l=0 #物流箱

#先把原圖放入input 產生以箱子為中心3840X3840正方形圖片
rcam = 'E:\\R_CAM\\'
tcam = 'F:\\T_CAM\\'
lcam = 'G:\\L_CAM\\'

output="H:\\OCR_test\\"

rcam_noread="E:\\OCR_Noread_box\\"
rcam_SBS="E:\\OCR_SBS\\"
rcam_flowbox='E:\\OCR_flow_box\\'

tcam_noread="F:\\OCR_Noread_box\\"
tcam_SBS="F:\\OCR_SBS\\"
tcam_flowbox='F:\\OCR_flow_box\\'

lcam_noread="G:\\OCR_Noread_box\\"
lcam_SBS="G:\\OCR_SBS\\"
lcam_flowbox='G:\\OCR_flow_box\\'

today = datetime.datetime.now().strftime("%Y-%m-%d")

conn = sqlite3.connect('D:\\Partdata\\database.db')
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS imglist (filename, CAM)''')

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

def cut(input:str, noread:str, sbs:str, flowbox:str, output_path) -> None: 
    #print("新圖片")
    global i
    global j
    global k
    global l
    while True:
        for filename in os.listdir(input):
            i+= 1
            try:
                conn = sqlite3.connect('D:\\Partdata\\database.db')
                cur = conn.cursor()
                cur.execute('pragma busy_timeout=10000')
                num = filename.find('Cam')
                cam = filename[num-2:num+3]
                cur.execute('''INSERT INTO imglist(filename, CAM)
                            VALUES (?, ?)''', (filename, cam))
                conn.commit()
            except Exception:
                conn.rollback()
            finally:
                conn.close()
            
            try:
                image_path_file = input + filename #路徑
                img_flow = cv2.imread(image_path_file) #讀取圖片
                
                if "NOREAD" in filename: #NoReadBox
                    j+=1
                    cv2.imwrite(noread + filename ,img_flow)
                    os.remove(input + filename)
                    
                elif "_1_" in filename: #併箱
                    k+=1
                    cv2.imwrite(sbs + filename ,img_flow)
                    os.remove(input + filename)
                elif len(filename)>=56: #flow box
                    l+=1
                    cv2.imwrite(flowbox + filename ,img_flow)
                    os.remove(input + filename)
                else:
                    if filename.endswith(".jpg"):
                        start=time.time()

                        img0 = cut_box(img_flow) #切箱
                        img0 = cv2.rotate(img0, cv2.ROTATE_90_CLOCKWISE) #轉90度
                        img0 = trans_square(img0) #轉成正方形並填充
                        img0 = cv2.resize(img0, (3840,3840)) #設定圖片大小3840x3840
                        output_file = output_path + filename 
                        cv2.imwrite(output_file, img0) #寫入
                        os.remove(image_path_file) #移除原始照片
                        end=time.time()
                        t=int((end-start)*1000)
                        print(str(img0.shape) + "辨識圖片總數= "+ str(i)+", NOREAD="+ str(j)+", 併箱="+ str(k) + ", 物流箱="+ str(l)+ ", time=" + str(t))

            except: pass
    #print("1111111111111111111")  
    #time.sleep(1)
    #cut(input, noread, sbs, flowbox)
       

             
def task():
    #on_timer()
    timer=threading.Timer(5,cut)    
    timer.start()
    time.sleep(6)
    timer.cancel()
    print("等待新圖片")


if __name__=='__main__':
    multiprocessing.freeze_support()
    while True:
        mp1 = multiprocessing.Process(target = cut, args = (rcam, rcam_noread, rcam_SBS, rcam_flowbox, output))
        mp2 = multiprocessing.Process(target = cut, args = (tcam, tcam_noread, tcam_SBS, tcam_flowbox, output))
        mp3 = multiprocessing.Process(target = cut, args = (lcam, lcam_noread, lcam_SBS, lcam_flowbox, output))
        mp1.start()
        mp2.start()
        mp3.start()
        mp1.join()
        mp2.join()
        mp3.join()