import json

from datetime import datetime
from dateutil import parser
from urllib import request
from flask import Flask, render_template, url_for

app = Flask(__name__)


class Day:
    def __init__(self, day, time_slots, people, day_number):
        self.day = day
        self.time_slots = time_slots
        self.people = people
        self.day_number = day_number


@app.route('/')
def index():
    open_status = get_json_from_url("http://cafeanalog.dk/api/open")
    shifts = get_json_from_url("http://cafeanalog.dk/api/shifts")

    gif = url_for('static', filename='gif/open/giphy.gif')
    model = {
        "gif": gif,
        "open": open_status["open"],
        "schedule":
            convert_json_shift_to_days(shifts)
    }
    return render_template('index.html', model=model)


def get_json_from_url(url):
    webURL = request.urlopen(url)
    data = webURL.read()
    encoding = webURL.info().get_content_charset('utf-8')
    return json.loads(data.decode(encoding))


def convert_json_shift_to_days(shifts):
    days = {}
    for shift in shifts:
        open = parser.parse(shift["Open"])
        close = parser.parse(shift["Close"])
        day = open.strftime("%a")
        day_number = open.strftime('%d')
        open_string = open.strftime('%H:%M')
        close_string = close.strftime('%H:%M')
        days\
            .setdefault(day, Day(day=day, time_slots=set(), people=set(), day_number=day_number))\
            .time_slots.update([open_string, close_string])

    for day in days.values():
        time_slots = day.time_slots
        minimum = min(time_slots)
        maximum = max(time_slots)
        new = time_slots.copy()
        for time in time_slots:
            if minimum < time < maximum:
                new.remove(time)

        day.time_slots = sorted(new)

    return sorted(days.values(), key=lambda x: x.day_number)

if __name__ == '__main__':
    app.debug = True
    app.run()
