from app import app, socketio

if __name__ == '__main__':
    # Running on all network interfaces on port 5000 in debug mode.
    socketio.run(app, host='0.0.0.0', port=3000, debug=True)

