import pandas as pd
import re

dfitno = pd.read_excel("C:\\AI_exp\\HP\\Partdata\\itfpara_POC.xlsx",index_col="外箱條碼") 

def date_check(itemnumber, itemdate ):
    num = itemdate.find("202")
    try:#無資料預設YYMD
        datetype=str(dfitno.loc[itemnumber]["日期格式"])
        if datetype=='nan':  
            datetype="YYMD"
    except:
            datetype="YYMD"   
    special_type = ['YYM', 'MYY', 'CMD', 'CSMSD', 'CSMD', 'DEYY',
                     'YYSMSD', "YSMSD", 'KHI', 'KH', 'YM']
#==YYMD=============================================
    if datetype=="YYMD" and len(itemdate[num:]) >= 8 and num >= 0: 
            itemdate = itemdate[num:]
            years=itemdate[0:4]
            months =itemdate[4:6]
            days=itemdate[6:8]
#==DMYY==============================================
    elif datetype=="DMYY" and len(itemdate) >= 8:
        years=(itemdate[4:8])
        months = (itemdate[2:4])                  
        days=(itemdate[0:2])
#==MDYY==============================================    
    elif datetype=="MDYY"and len(itemdate) >= 8:
        years=itemdate[4:8]          
        months=itemdate[0:2]        
        days=itemdate[2:4]
#==DMY==============================================           
    elif datetype=="DMY"and len(itemdate) >= 6:
        year = int(itemdate[4:6])
        years = str(2000 + year)                   
        months = itemdate[2:4]  
        days=itemdate[0:2] 
#=YMD=======================================
    elif datetype=="YMD"and len(itemdate) >= 6:
        year = int(itemdate[0:2])
        years = str(2000 + year)                 
        months = itemdate[2:4]
        days=itemdate[4:6]   
#==special datetype================================                
    elif datetype in special_type and len(itemdate)>=8:
        years = int(itemdate[0:4])                   
        months = int(itemdate[4:6]) 
        days=int(itemdate[6:8])
    else: 
        years, months, days = '-1', '-1', '-1'
#判斷日月年是否正確===========================================     
    if int(years) in range(2023, 2030) and int(months) in range(1, 13) and int(days) in range(1, 32):
        exp = years + months + days 
        expmessge = "TXT_OK"
    else:
        exp="EXP_not_idfy"
        expmessge = "TXT_NG" 
        print('TXT ERROR')     
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
        return txts
    elif datetype == 'CMD' or datetype =='CSMSD'or datetype =='CSMD' and len(txts)>=5: #113.1.30
        txts = txts[txts.find('11'): ]
        txts_split = re.split('\D+', txts)
        y,m,d = txts_split[0], txts_split[1], txts_split[2]
        year = int(y)+1911
        month = ['0'+m if len(m)==1 else m]
        day = ['0'+d if len(d)==1 else d]
        txts = str(year)+month[0]+day[0]
        return txts
    elif datetype == 'YYM' or datetype =='MYY' and len(txts)>=5: #2024.01 or 2024 01 or 01.2024 or 01 2024
        txts = re.sub('\D+', '', txts)
        if datetype == 'YYM': #202401
            txts = txts[0:4]+txts[4:6]+'01'
        if datetype == 'MYY': #012024
            txts = txts[2:6]+txts[0:2]+'01'
        return txts
    elif datetype == 'YYSMSD' or datetype =='YSMSD'  and len(txts)>=6: #2024.1.1 or 24.1.1
        txts = txts[txts.find('2'): ]
        txts_split = re.split('\D+', txts)
        y,m,d = txts_split[0], txts_split[1], txts_split[2]
        year = [int(y)+2000 if datetype=='YSMSD' else int(y)]
        month = ['0'+m if len(m)==1 else m]
        day = ['0'+d if len(d)==1 else d]
        txts = str(year[0])+month[0]+day[0]
        return txts
    elif datetype == 'YM' and len(txts) >= 3: #24.1 or 24.10
        txts = txts[txts.find('2'): ]
        txts_split = re.split('\D+', txts)
        y,m = txts_split[0], txts_split[1]
        year = int(y)+2000
        month = ['0'+m if len(m)==1 else m]
        txts = str(year)+month[0]+'01'
        return txts
    elif datetype == 'KHI' and len(txts)>=7: #2024K01H30I 2024年01月30日 or 2024年1月30日 
        txts = txts[txts.find('20'): ]
        txts_split = re.split('\D+', txts)
        y,m,d = txts_split[0], txts_split[1], txts_split[2]
        year = int(y)
        month = ['0'+m if len(m)==1 else m]
        day = ['0'+d if len(d)==1 else d]
        txts = str(year)+month[0]+day[0]
        return txts
    elif datetype == 'KH' and len(txts)>= 6: #2024K10H 2024年1月 or 2024年10月
        txts = txts[txts.find('20'): ]
        txts_split = re.split('\D+', txts)
        y,m = txts_split[0], txts_split[1]
        year = int(y)
        month = ['0'+m if len(m)==1 else m]
        txts = str(year)+month[0]+'01'
        return txts
    else:
        return txts