import os
from time import localtime, mktime
from datetime import datetime , date
from flask import Flask, render_template, abort, redirect, request, url_for, flash
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SECRET_KEY'] = 'thisisasecretkeyoncethisgoeslivenoreallyipromise'

db = SQLAlchemy(app)

class Rooms(db.Model):
    __tablename__ = 'getapod_rooms'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    pods = db.Column(db.Integer)

    def __init__(self, name, pods):
        self.name = name
        self.pods = pods

class Bookings(db.Model):
    __tablename__ = 'getapod_bookings'
    id = db.Column(db.Integer, primary_key=True)
    room = db.Column(db.Integer)
    time = db.Column(db.Integer)
    pod = db.Column(db.Integer)
    duration = db.Column(db.Integer)
    name1 = db.Column(db.String(64))
    name2 = db.Column(db.String(64), nullable=True)
    comment = db.Column(db.String(64), nullable=True)
    flag = db.Column(db.String(64))

    def __init__(self, room, time, pod, duration, name1, name2, comment, flag):
        self.room = room
        self.time = time
        self.pod = pod
        self.duration = duration
        self.name1 = name1
        self.name2 = name2
        self.comment = comment
        self.flag = flag

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
    '''Returns a dictionary with todays date +/- returned as string and epoch_s'''
    today_s = date_to_sec(today_d)
    yday_s = today_s-86400
    yday_d = sec_to_date(yday_s)
    morrow_s = today_s+86400
    morrow_d = sec_to_date(morrow_s)
    
    return { 'today': { 'string': today_s, 'date': today_d },
             'yesterday': { 'string': yday_s, 'date': yday_d },
             'tomorrow': { 'string': morrow_s, 'date': morrow_d } 
           }

def get_bookings(roomdata, epoch):
    booking_data = {}
    hours = [8,10,13,15,17,19,21]
    for hour in hours:
        booking_data[hour] = {}
        for pod in range(1, roomdata.pods+1):
            data = Bookings.query.filter(Bookings.time==(epoch+(hour*3600))).filter(Bookings.room==roomdata.id).filter(Bookings.pod==pod).all()
            if len(data) >= 1:
                booking_data[hour][pod] = f'<a href="/delete/{roomdata.name}/{sec_to_date(epoch+(hour*3600))}/{hour}/{chr(pod+64)}"> \
                    {data[0].name1}</a><br>{data[0].name2}<br>{data[0].comment}'
            else:
                booking_data[hour][pod] = f'<a href="/book/{roomdata.name}/{sec_to_date(epoch+(hour*3600))}/{hour}/{chr(pod+64)}">Get POD!</a>'
    return booking_data

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/show/<room>')
@app.route('/show/<room>/<caldate>')
def show(room, caldate='Null'):
    
    if room.upper() not in 'B112 B113 B114 B118 B123 B125':
        abort(404, description="Resource not found")
    
    if caldate == 'Null':
        today_d = str(date.today())[2:]
    else:
        today_d = caldate
    
    dates = init_dates(today_d)
    
    show = {}
    roomdata = Rooms.query.filter(Rooms.name==room.upper()).all()[0]
    show['room'] = {'name': roomdata.name.upper(), 'pods': [chr(x+65) for x in range(roomdata.pods)]}
    show['dates'] = dates
    show['clocks'] = [8,10,13,15,17,19,21]
    #bookingdata = Bookings.query.filter(Bookings.time > today).filter(Bookings.time < tomorrow).all()
    show['query'] = get_bookings(roomdata, dates['today']['string'])

    return render_template('show.html', show=show, test='<hr>')

@app.route('/book')
@app.route('/book/<room>')
@app.route('/book/<room>/<caldate>')
@app.route('/book/<room>/<caldate>/<hr>/<pod>', methods=('GET', 'POST'))
def book(room='Null', caldate='Null', hr='Null', pod='Null'):
    if request.method == 'POST':
        namn1 = request.form['namn1']
        roomdata = Rooms.query.filter(Rooms.name==room.upper()).all()[0]
        book_time = date_to_sec(caldate) + (3600 * int(hr))
        bi = Bookings(
                room=roomdata.id,
                time=book_time,
                pod=ord(pod.upper())-64,
                duration=2,
                name1=namn1,
                name2='',
                comment='',
                flag='AVAILABLE'
                )
        db.session.add(bi)
        db.session.commit()
        return redirect(f"/show/{roomdata.name.upper()}/{caldate}", code=302)

    if 'Null' in locals().values():
        return redirect("/show/B112", code=302)
    else:
        roomdata = Rooms.query.filter(Rooms.name==room.upper()).all()[0]
        if int(hr) in [8,10,13,15,17,19,21]:
            return render_template('book.html', data=locals())
        else:
            return redirect(f"/show/{roomdata.name.upper()}", code=302)

@app.route('/delete/<hash>')
def delete(hash):
    return True


if __name__ == "__main__":
    app.run(debug=True)