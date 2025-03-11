from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import json
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

DATA_FILE = "data.json"

# Load existing data if available, otherwise initialize data_store
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data_store = json.load(f)
else:
    data_store = {
        "names": [],
        "checkins": {}
    }

def save_data():
    """Save the data_store to a JSON file."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data_store, f, indent=4, ensure_ascii=False)

@socketio.on('connect')
def handle_connect():
    # When a client connects, send the stored data (names and checkins)
    emit("initial_data", data_store)

@socketio.on('message')
def handle_message(message):
    action = message.get("action")
    if action == "update_names":
        names = message.get("names", [])
        data_store["names"] = names
        print("Name list updated:", names)
        save_data()
        emit("message", {"info": "Name list updated"}, broadcast=True)
    elif action == "checkin":
        day = message.get("day")
        name = message.get("name")
        remark = message.get("remark", "")
        # Set status explicitly: "remark" if a remark exists, else "checkin"
        status = "remark" if remark else "checkin"
        record = {"name": name, "remark": remark, "status": status}
        if day not in data_store["checkins"]:
            data_store["checkins"][day] = []
        data_store["checkins"][day].append(record)
        print(f"{name} checked in on day {day} with remark: {remark}")
        save_data()
        emit("message", {"info": f"{name} checked in on day {day}"}, broadcast=True)
    elif action == "cancel":
        day = message.get("day")
        name = message.get("name")
        if day in data_store["checkins"]:
            for record in data_store["checkins"][day]:
                if (isinstance(record, dict) and record.get("name") == name) or (isinstance(record, str) and record == name):
                    data_store["checkins"][day].remove(record)
                    break
            print(f"{name}'s check-in on day {day} canceled")
            save_data()
            emit("message", {"info": f"{name}'s check-in on day {day} canceled"}, broadcast=True)
    elif action == "toggle_status":
        day = message.get("day")
        name = message.get("name")
        if day in data_store["checkins"]:
            for record in data_store["checkins"][day]:
                if isinstance(record, dict) and record.get("name") == name:
                    # Update the status to "checkin" without clearing the remark.
                    record["status"] = "checkin"
                    print(f"Record for {name} on day {day} toggled to checkin status")
                    save_data()
                    emit("message", {"info": f"Record for {name} on day {day} toggled to checkin status"}, broadcast=True)
                    break
    else:
        print("Unknown action:", action)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    socketio.run(app, debug=True)

