from cgitb import html
from time import localtime, mktime, time
from datetime import datetime, date
import calendar
from calendar import HTMLCalendar

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

def date_start_epoch(epoch):
    '''Returns the unixtime of the start of the day, for +hour manipulation'''
    dt = datetime.date(datetime.fromtimestamp(epoch))
    return mktime(dt.timetuple())

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

def check_book_epoch(epoch, minutes):
    '''Booking possible if within # minutes of pod timeslot start'''
    now_s = round(time())
    if epoch > now_s:
        return True
    elif epoch < now_s and abs(epoch - now_s) < (minutes*60):
        return True
    else:
        return False

def epoch_hr(epoch):
    '''Checks if a timestamp is within a grace period of the booking-time'''
    if isinstance(epoch, int) or isinstance(epoch, float):
        return datetime.fromtimestamp(epoch).hour
    elif epoch == 'HR':
        return datetime.fromtimestamp(time()).hour
    elif epoch == 'NOW':
        return time()

def date_to_str():
    '''Todays date but without the leading 2 digits in 2022'''
    return str(date.today())[2:]

def show_calendar(urldate, room):
    
    class RoomCalendar(HTMLCalendar):
        def __init__(self, today=[], *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._today = today
 
        def formatday(self, day, weekday):
            today = datetime.now()
            daystr = f'{str(today.year)[2:]}-{today.month}-{day}'
            url = 'http://localhost:5000/show/ROOM/'
            if day == self._today:
                return f'<td class="today"><a href="{url}{daystr}" class="calurl">{day}</a></td>'
            elif day == 0:
                return '<td class="noday">&nbsp;</td>'
            else:
                return f'<td class="wday"><a class="calurl" href="{url}{daystr}">{day}</a></td>'

    urldate = [int(x) for x in urldate.split('-')]
    today_date = datetime.now()
    html_raw = RoomCalendar(today=today_date.day).formatmonth(2000+urldate[0], urldate[1], withyear=False)
    html_output = ''
    for line in html_raw.split('\n'):
        if 'month' not in line and 'table' not in line:
            if 'class="mon"' in line:
                line = '<tr><th class="dh">M</th><th class="dh">T</th><th class="dh">W</th><th class="dh">T</th><th class="dh">F</th><th class="dh">S</th><th class="dh">S</th></tr>'
            if 'class="today"' in line:
                line = line.replace('class="today"', 'class="today table-success"')
            html_output += line
    html_output = html_output.replace('ROOM', room)
    return html_output





