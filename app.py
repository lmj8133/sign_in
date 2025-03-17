from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import json
import os

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

DATA_FILE = "data.json"

# Load existing data if available; otherwise initialize data_store
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data_store = json.load(f)
else:
    data_store = {
        "names": [],
        "checkins": {}
    }

def save_data():
    # Save data_store to a JSON file
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data_store, f, indent=4, ensure_ascii=False)

def get_date_key(year, month, day):
    # Construct a date key in the format "YYYY-MM-DD". Note: month from frontend is zero-indexed.
    return f"{year}-{int(month)+1:02d}-{int(day):02d}"

@socketio.on('connect')
def handle_connect():
    # Send stored names and check-ins when a client connects
    emit("initial_data", data_store)

@socketio.on('get_month_data')
def handle_get_month_data(message):
    year = message.get("year")
    month = message.get("month")
    month_prefix = f"{year}-{int(month)+1:02d}-"
    # Filter check-ins for keys that start with the month prefix
    month_data = { key: val for key, val in data_store["checkins"].items() if key.startswith(month_prefix) }
    emit("month_data", month_data)

@socketio.on('message')
def handle_message(message):
    action = message.get("action")
    if action == "update_names":
        # Expect names as a list of objects: {"name": "...", "added_hours": ...}
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
        status = "checkin"  # Force status to "checkin"
        # Read hours (default to 1 if not provided)
        hours = message.get("hours", 1)
        record = {"name": name, "remark": remark, "status": status, "hours": hours}
        if date_key not in data_store["checkins"]:
            data_store["checkins"][date_key] = []
        updated = False
        old_hours = 0
        current_record = None
        # Check if there is already a record for this user on the given day
        for rec in data_store["checkins"][date_key]:
            if isinstance(rec, dict) and rec.get("name") == name:
                old_hours = rec.get("hours", 0)
                rec["remark"] = remark
                rec["status"] = status
                rec["hours"] = hours  # Update hours
                current_record = rec
                updated = True
                break
        if not updated:
            data_store["checkins"][date_key].append(record)
            current_record = record

        # Update cumulative hours (added_hours) for the user in the names list
        for u in data_store["names"]:
            if u["name"] == name:
                if updated:
                    u["added_hours"] = u.get("added_hours", 0) + (hours - old_hours)
                else:
                    u["added_hours"] = u.get("added_hours", 0) + hours
                # If cumulative hours are >= 4, mark checkbox and subtract 4 hours
                if u["added_hours"] >= 4:
                    current_record["checkbox"] = 1
                    u["added_hours"] -= 4
                else:
                    current_record["checkbox"] = 0
                break

        print(f"{name} checked in on {date_key} with remark: {remark} and hours: {hours}")
        save_data()
        emit("message", {"info": f"{name} checked in on {date_key} (hours: {hours})"}, broadcast=True)

    elif action == "remark":
        year = message.get("year")
        month = message.get("month")
        day = message.get("day")
        date_key = get_date_key(year, month, day)
        name = message.get("name")
        remark = message.get("remark", "")
        status = "remark"  # Force status to "remark"
        record = {"name": name, "remark": remark, "status": status}
        if date_key not in data_store["checkins"]:
            data_store["checkins"][date_key] = []
        updated = False
        for rec in data_store["checkins"][date_key]:
            if isinstance(rec, dict) and rec.get("name") == name:
                rec["remark"] = remark
                rec["status"] = status
                updated = True
                break
        if not updated:
            data_store["checkins"][date_key].append(record)
        print(f"{name} checked in with remark on {date_key}: {remark}")
        save_data()
        emit("message", {"info": f"{name} checked in with remark on {date_key}"}, broadcast=True)

    elif action == "cancel":
        year = message.get("year")
        month = message.get("month")
        day = message.get("day")
        date_key = get_date_key(year, month, day)
        name = message.get("name")
        if date_key in data_store["checkins"]:
            for record in data_store["checkins"][date_key]:
                if isinstance(record, dict) and record.get("name") == name:
                    # If record is a checkin with hours, deduct its hours from cumulative hours
                    if record.get("status") == "checkin" and "hours" in record:
                        hrs = record["hours"]
                        for u in data_store["names"]:
                            if u["name"] == name:
                                u["added_hours"] = u.get("added_hours", 0) - hrs
                                # If cumulative hours are < 0, add 4 hours back
                                if u["added_hours"] < 0:
                                    u["added_hours"] = u.get("added_hours", 0) + 4
                                break
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
        new_status = message.get("status")  # Expected to be "checkin" or "remark"
        if date_key in data_store["checkins"]:
            for record in data_store["checkins"][date_key]:
                if isinstance(record, dict) and record.get("name") == name:
                    record["status"] = new_status
                    print(f"Record for {name} on {date_key} toggled to {new_status} status")
                    save_data()
                    emit("message", {"info": f"Record for {name} on {date_key} toggled to {new_status} status"}, broadcast=True)
                    break

    elif action == "update_remark":
        year = message.get("year")
        month = message.get("month")
        day = message.get("day")
        date_key = get_date_key(year, month, day)
        name = message.get("name")
        new_remark = message.get("remark")
        if date_key in data_store["checkins"]:
            for record in data_store["checkins"][date_key]:
                if isinstance(record, dict) and record.get("name") == name:
                    record["remark"] = new_remark
                    print(f"Remark for {name} on {date_key} updated to: {new_remark}")
                    save_data()
                    emit("message", {"info": f"Remark for {name} on {date_key} updated"}, broadcast=True)
                    break

    elif action == "toggle_checkbox":
        #update checkbox status
        year = message.get("year")
        month = message.get("month")
        day = message.get("day")
        date_key = get_date_key(year, month, day)
        name = message.get("name")
        checkbox = message.get("checkbox")
        if date_key in data_store["checkins"]:
            for record in data_store["checkins"][date_key]:
                if isinstance(record, dict) and record.get("name") == name:
                    record["checkbox"] = checkbox
                    print(f"Checkbox for {name} on {date_key} toggled to {checkbox}")
                    save_data()
                    emit("message", {"info": f"Checkbox for {name} on {date_key} toggled to {checkbox}"}, broadcast=True)
                    break

    else:
        print("Unknown action:", action)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=3000, debug=True, use_reloader=False)

