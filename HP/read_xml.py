import xml.etree.ElementTree as ET
import sqlite3
import os

path = 'D:\\Partdata\\xml\\'

def convert_xml(filepath:str) -> None:
    '''將XML檔轉換並寫入SQLite'''
    tree = ET.parse(filepath)
    root = tree.getroot()
    filename = filepath[filepath.find('sorter'): ]
    
    for i in root.findall('doc'):
        item_no = i.find('ITEM_NO').text
        cusc_chuteid = i.find('CUSC_CHUTEID').text
        ijp = i.find('IJP').text
        barcode = i.find('BARCODE1').text
        sysno = i.find('SYSNO').text

        try:
            conn = sqlite3.connect('D:\\PartData\\database.db')
            cur = conn.cursor()
            cur.execute('pragma busy_timeout=10000')
            cur.execute('''CREATE TABLE IF NOT EXISTS xml (ITEM_NO TEXT, 
            CUSC_CHUTEID INT, IJP TEXT, BARCODE TEXT, SYSNO TEXT, filename TEXT)''')
            cur.execute('INSERT INTO xml VALUES (?,?,?,?,?,?)', 
                        (item_no, cusc_chuteid, ijp, barcode, sysno, filename))
            conn.commit()
        except: 
            conn.rollback()
        finally:
            conn.close()
    print('已執行', filepath)
    
    #os.replace(filepath, )
