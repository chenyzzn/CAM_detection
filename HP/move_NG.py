#move file
from shutil import move
import datetime
import os

today = datetime.date.today()

def move_NG(CAM:str) -> None:
    try:
        if CAM == 'RCAM':
            path1 = 'E:\\OCR_EXP_NG\\'
        elif CAM == 'TCAM':
            path1 = 'F:\\OCR_EXP_NG\\'
        elif CAM == 'LCAM':
            path1 = 'G:\\OCR_EXP_NG\\'
        path2 = f'D:\\NG_img\\{CAM}_{today}'
        if not os.path.isdir('D:\\NG_img'): os.mkdir('D:\\NG_img')
        if not os.path.isdir(path2): os.mkdir(path2)
        move(path1, path2)
        os.mkdir(path1)
    except: pass

if __name__ == '__main__':
    move_NG('RCAM')
    move_NG('TCAM')
    move_NG('LCAM')