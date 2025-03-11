from app import app, socketio
import webbrowser

def open_browser():
    webbrowser.open("http://127.0.0.1:3000")

if __name__ == '__main__':
    socketio.start_background_task(open_browser)
    socketio.run(app, host='0.0.0.0', port=3000, debug=True, use_reloader=False)

