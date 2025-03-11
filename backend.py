from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Store check-in records: format { 'day': [name1, name2, ...] }
checkin_records = {}

@app.route('/')
def index():
    return render_template('index.html')  # Front-end HTML file

@socketio.on('message')
def handle_message(message):
    data = json.loads(message)
    action = data.get("action")
    day = data.get("day")
    name = data.get("name")
    if action == "checkin":
        if day not in checkin_records:
            checkin_records[day] = []
        checkin_records[day].append(name)
        print(f"{name} checked in on day {day}")
        # Broadcast message to all connected clients to update the UI
        emit("message", f"{name} checked in on day {day}", broadcast=True)
    elif action == "cancel":
        if day in checkin_records and name in checkin_records[day]:
            checkin_records[day].remove(name)
            print(f"{name} check-in on day {day} canceled")
            emit("message", f"{name} check-in on day {day} canceled", broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)

