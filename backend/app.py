from flask import Flask, g, request, send_from_directory
import sqlite3

app = Flask(__name__)

DATABASE = '/home/luka/Desktop/haoma.db'


def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE, isolation_level=None)
        db.row_factory = make_dicts
    return db


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/patient')
def get_patient():
    response = []
    patient_key = request.values['patient_key']
    patient_key += '%'
    print(patient_key)
    for row in query_db("SELECT * FROM Patients WHERE patient_key LIKE '" + patient_key + "'"):
        response.append(row)
    return str(response[0])


@app.route('/measurement', methods=['GET'])
def get_measurement():
    response = []
    for row in query_db('SELECT * FROM WaitingRoomMeasuremnets ORDER BY timestamp DESC LIMIT 1'):
        response.append(row)
    if len(response) == 0:
        return 'No measurements taken'
    return str(response[0])


@app.route('/measurement_dist')
def get_measurement_dist():
    response = []
    for row in query_db('''
    SELECT AVG(acceleration) AS avg_acc,
       SUM((acceleration-(SELECT AVG(acceleration) FROM WaitingRoomMeasuremnets))*
           (acceleration-(SELECT AVG(acceleration) FROM WaitingRoomMeasuremnets)) ) / (COUNT(acceleration)-1) AS stdev_acc,
       AVG(gyromotion) AS avg_gyro,
       SUM((gyromotion-(SELECT AVG(gyromotion) FROM WaitingRoomMeasuremnets))*
           (gyromotion-(SELECT AVG(gyromotion) FROM WaitingRoomMeasuremnets)) ) / (COUNT(gyromotion)-1) AS stdev_gyro,
       AVG(temperature) AS avg_temp,
       SUM((temperature-(SELECT AVG(temperature) FROM WaitingRoomMeasuremnets))*
           (temperature-(SELECT AVG(temperature) FROM WaitingRoomMeasuremnets)) ) / (COUNT(temperature)-1) AS stdev_temp,
       AVG(humidity) AS avg_hum,
       SUM((humidity-(SELECT AVG(humidity) FROM WaitingRoomMeasuremnets))*
           (humidity-(SELECT AVG(humidity) FROM WaitingRoomMeasuremnets)) ) / (COUNT(humidity)-1) AS stdev_hum,
       AVG(volume) AS avg_vol,
       SUM((volume-(SELECT AVG(volume) FROM WaitingRoomMeasuremnets))*
           (volume-(SELECT AVG(volume) FROM WaitingRoomMeasuremnets)) ) / (COUNT(volume)-1) AS stdev_vol
    FROM WaitingRoomMeasuremnets
    WHERE CAST(strftime('%s', timestamp) AS INT) < CAST(strftime('%s', '2019-09-08 05:45:33') AS INT)'''):
        response.append(row)
    if len(response) == 0:
        return 'No measurements taken'
    return str(response[0])


@app.route('/measurement', methods=['POST'])
def post_measurement():
    print(request.values)
    motion = request.values['motion']
    acceleration = request.values['acceleration']
    gyromotion = request.values['gyromotion']
    temperature = request.values['temperature']
    humidity = request.values['humidity']
    volume = request.values['volume']
    print(motion, acceleration, gyromotion, temperature, humidity, volume)
    query_db(
        'INSERT INTO WaitingRoomMeasuremnets (motion, acceleration, gyromotion, temperature, humidity, volume) ' +
        'VALUES (?, ?, ?, ?, ?, ?)',
        (motion, acceleration, gyromotion, temperature, humidity, volume))
    return "Ok!"

@app.route('/realtime_measurements')
def realtime_measurements():
    return send_from_directory('static', 'index.html')


if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host='0.0.0.0', port=1337, debug=True)
