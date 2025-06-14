from flask import Flask, render_template, request, redirect, url_for
from tinydb import TinyDB, Query
from datetime import datetime, timedelta

app = Flask(__name__)
db = TinyDB('db.json')
query = Query()

@app.route('/', methods=['GET'])
def index():
    now = datetime.now()
    all_entries = db.all()

    # Auto-update expired validation
    for entry in all_entries:
        end_time_str = entry.get('EndTime')
        end_dt = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")
        if end_dt < now and entry.get('Validation') is True:
            db.update({'Validation': False}, (query.EndTime == end_time_str) & (query.Name == entry['Name']))

    class_id = request.args.get('filter_class')
    show_all = request.args.get('show_all')

    if show_all:
        valid_data = db.search(query.Validation == True)
        expired_data = db.search(query.Validation == False)
    elif class_id:
        valid_data = db.search((query.Validation == True) & (query.ClassID == class_id))
        expired_data = db.search((query.Validation == False) & (query.ClassID == class_id))
    else:
        valid_data = []
        expired_data = []

    return render_template('index.html', data=valid_data, expired=expired_data)





@app.route('/add', methods=['POST'])
def add():
    name = request.form.get('name')
    delta_minutes = request.form.get('endTime')
    class_id = request.form.get('classID')

    try:
        delta_minutes = int(delta_minutes)
    except ValueError:
        delta_minutes = 0

    start_dt = datetime.now()
    end_dt = start_dt + timedelta(minutes=delta_minutes)

    validation = end_dt > start_dt
    start_time = start_dt.strftime('%Y-%m-%d %H:%M:%S')
    end_time = end_dt.strftime('%Y-%m-%d %H:%M:%S')

    db.insert({
        'Name': name,
        'StartTime': start_time,
        'EndTime': end_time,
        'Validation': validation,
        'ClassID': class_id
    })

    return redirect(url_for('index', filter_class=class_id))


@app.route('/delete', methods=['POST'])
def delete():
    name = request.form.get('name')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')

    db.remove((query.Name == name) & (query.StartTime == start_time) & (query.EndTime == end_time))
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(port=1107, debug=True)
