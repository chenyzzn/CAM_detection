import cv2
import os
import tkinter as tk
import tkinter as ttk
#from watchdog.observers import Observer
#from watchdog.events import FileSystemEventHandler
import numpy as np
import time
import threading
i=0
j=0
T=0
#先把原圖放入 input 產生以箱子為中心1920X1920正方形圖片
input_dir="F:\\T_CAM\\" #R_CAM\\
output_dir="F:\\OCR_test\\"
if not os.path.isdir(output_dir): os.mkdir(output_dir)
output_NoRead_file="F:\\OCR_Noread_box\\"
output_SBS="F:\\OCR_SBS\\"
def cut_box(img0):
        
            img=img0
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            ret, img = cv2.threshold(img, 80, 255, cv2.THRESH_BINARY)
            contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            areas = [cv2.contourArea(c) for c in contours]#1
            max_index = areas.index(max(areas))#2
            max_rect =cv2.minAreaRect(contours[max_index])#3
            max_box = cv2.boxPoints(max_rect)#4
            #max_box = np.int0(max_box)#5
            x, y, h, w =cv2.boundingRect(max_box) #取得包覆指定輪廓點的最小正矩形 #b = event.key[1].split("_") #分割符號為 "-"
            if x>=0 and y>=0 : img0 = img0[y:y+w, x: x+h] #裁切所需要的範圍 #imgy=img0.shape[0]      #imgx=img0.shape[1]   #if imgy > imgx  : 
            return img0
        
            #裁切=====================================================   
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
        #cv2.imshow("a",img)
        #cv2.waitKey(0)

    return img

#class MyOcrEventHanlder(FileSystemEventHandler):
def on_timer(): #self裡面是參數指標event是大部分參數
    print("新圖片")
    #time.sleep(0.1)
    global path_filename
    global i
    global j
    #list=os.listdir(input_dir)
    #list_T= os.listdir("D:\\T_CAM\\")
    l=bool(os.listdir(input_dir))
    #for fl in os.listdir("D:\\T_CAM\\"):
    #os.remove("D:\\T_CAM\\" + fl)
    
    for filename in os.listdir(input_dir):
        lens=len(filename)
        T=0
        if "NOREAD" in filename:# or lens > 52 or lens < 50  :
            i=i+1
            j=j+1
            try:
                image_path_file = input_dir + filename
                img_flow = cv2.imread(image_path_file)

                cv2.imwrite(output_NoRead_file + filename ,img_flow)#訓練用圖片
                os.remove(input_dir + filename)
            except:
                pass    
        elif "_1_" in filename: 
            i=i+1
            j=j+1
            try:
                image_path_file = input_dir + filename
                img_flow = cv2.imread(image_path_file)
                cv2.imwrite(output_SBS + filename ,img_flow)#訓練用圖片
                os.remove(input_dir + filename)
            except:
                pass   
        else:
            if filename.endswith(".jpg") and "NOREAD" not in filename:
                start=time.time()
                image_path_file = input_dir + filename
                try:
                    img0 = cv2.imread(image_path_file)
                    #切箱
                    img0=cut_box(img0)
                    #轉90度
                    img0 = cv2.rotate(img0, cv2.ROTATE_90_CLOCKWISE)
                    #填充至1920X1920
                    img0 = trans_square(img0)
                    #img0 = cv2.resize(img0,(1920,1920))
                    img0 = cv2.resize(img0,(3840,3840))
                    im=cv2.resize(img0,(480,480))
                    #cv2.imshow("result",im)
                    #cv2.waitKey(1)
                    #寫入                       str(i)
                    output_file = output_dir + filename #+ filename 
                    cv2.imwrite(output_file,img0)
                    os.remove(image_path_file)
                    end=time.time()
                    t=int((end-start)*1000)
                    end=time.time()
                    i=i+1 
    
                    print(str(img0.shape) + "辨識圖片總數= "+ str(i)+" , NOREAD="+ str(j) + " ,time=" + str(t) )
                except:
                    pass
    task()
    print("1111111111111111111")     
               
def task():
    #on_timer()
    timer=threading.Timer(5,on_timer)    
    timer.start()
    time.sleep(6)
    timer.cancel()
    print("等待新圖片")


if __name__=='__main__':
    task()
    #time.sleep(5)
    #print("0ocr_y_p_1227.exe")
    #os.system("d:\\120\\dist\\0ocr_y_p_1227\\0ocr_y_p_1227.exe")
    #print("0ocr_y_p_1227.exe完成")
   # observer_ocr = Observer()# 创建观察者对象
   # file_Handler = MyOcrEventHanlder()# 创建事件处理对象
   # observer_ocr.schedule(file_Handler,input_dir,recursive=False)
   # observer_ocr.start()
   #timer=threading.Timer(2,on_timer)
   #timer.start()
   #time.sleep(1)
   #timer.cancel()
"""   
#視窗======================================================================
    
   win=tk.Tk()
   win.title('GUI')
   win.geometry('100x100+100+900')
   frm = ttk.Frame(win)#.pack(padx=100,pady=10)#,width=600, height=500, bg="blue").pack()
   frm.grid()
   ttk.Button(frm, text="Quit", command=win.destroy).grid(column=100, row=100)
   win.mainloop()
"""    
