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

def get_date_key(year, month, day):
    """
    Construct a date key in the format "YYYY-MM-DD".
    Note: the month value from the frontend is zero-indexed.
    """
    return f"{year}-{int(month)+1:02d}-{int(day):02d}"

@socketio.on('connect')
def handle_connect():
    # When a client connects, send the stored names and all checkins
    emit("initial_data", data_store)

@socketio.on('get_month_data')
def handle_get_month_data(message):
    year = message.get("year")
    month = message.get("month")
    month_prefix = f"{year}-{int(month)+1:02d}-"
    # Filter check-ins for keys that start with month_prefix
    month_data = { key: val for key, val in data_store["checkins"].items() if key.startswith(month_prefix) }
    emit("month_data", month_data)

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
        year = message.get("year")
        month = message.get("month")
        day = message.get("day")
        date_key = get_date_key(year, month, day)
        name = message.get("name")
        remark = message.get("remark", "")
        status = "remark" if remark else "checkin"
        record = {"name": name, "remark": remark, "status": status}
        if date_key not in data_store["checkins"]:
            data_store["checkins"][date_key] = []
        # Update if record exists; otherwise add new.
        updated = False
        for rec in data_store["checkins"][date_key]:
            if isinstance(rec, dict) and rec.get("name") == name:
                rec["remark"] = remark
                rec["status"] = status
                updated = True
                break
        if not updated:
            data_store["checkins"][date_key].append(record)
        print(f"{name} checked in on {date_key} with remark: {remark}")
        save_data()
        emit("message", {"info": f"{name} checked in on {date_key}"}, broadcast=True)
        
    elif action == "cancel":
        year = message.get("year")
        month = message.get("month")
        day = message.get("day")
        date_key = get_date_key(year, month, day)
        name = message.get("name")
        if date_key in data_store["checkins"]:
            for record in data_store["checkins"][date_key]:
                if isinstance(record, dict) and record.get("name") == name:
                    data_store["checkins"][date_key].remove(record)
                    break
            print(f"{name}'s check-in on {date_key} canceled")
            save_data()
            emit("message", {"info": f"{name}'s check-in on {date_key} canceled"}, broadcast=True)
            
    elif action == "toggle_status":
        year = message.get("year")
        month = message.get("month")
        day = message.get("day")
        date_key = get_date_key(year, month, day)
        name = message.get("name")
        if date_key in data_store["checkins"]:
            for record in data_store["checkins"][date_key]:
                if isinstance(record, dict) and record.get("name") == name:
                    # Toggle the status to "checkin" without clearing the remark.
                    record["status"] = "checkin"
                    print(f"Record for {name} on {date_key} toggled to checkin status")
                    save_data()
                    emit("message", {"info": f"Record for {name} on {date_key} toggled to checkin status"}, broadcast=True)
                    break
    else:
        print("Unknown action:", action)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    socketio.run(app, debug=True)

