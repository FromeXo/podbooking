from time import localtime, mktime
from datetime import datetime, date

def sec_to_date(sec):
    '''str_date returns in the format YY-M-D'''
    ds = localtime(sec)
    str_date = f'{str(ds.tm_year)[2:]}-{ds.tm_mon}-{ds.tm_mday}'
    return str_date

def date_to_sec(str_date):
    '''str_date should always be in the format YY-M-D
       returns the current yy-m-d in unix epoch seconds since 1970'''

    ld = [int(n) for n in str_date.split('-')]
    '''adds 2000 to fix year-trimming in date-format to avoid mktime() crash'''
    date = datetime(2000 + ld[0], ld[1], ld[2])
    sec = int(mktime(date.timetuple()))
    return sec

def init_dates(today_d):
    '''Returns a dictionary with todays date +/- 1 returned as string and epoch_s'''
    today_s = date_to_sec(today_d)
    yday_s = today_s-86400
    yday_d = sec_to_date(yday_s)
    morrow_s = today_s+86400
    morrow_d = sec_to_date(morrow_s)
    
    return { 'today': { 'string': today_s, 'date': today_d },
             'yesterday': { 'string': yday_s, 'date': yday_d },
             'tomorrow': { 'string': morrow_s, 'date': morrow_d } 
           }

def date_to_str():
    return str(date.today())[2:]