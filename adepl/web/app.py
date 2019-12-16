import os
from threading import Thread
from typing import Dict

from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO

from adepl.utils.rotary_files.reader import Reader

HTTP_PORT = 7895
ADEPL_DIR = "/tmp/adepl"
MAX_HISTORY_LENGTH = 1000

# run env initialization
RECOGNITION_SERVICE = None  # will be initialized later (due to process forking interference with flask)
os.makedirs(ADEPL_DIR, exist_ok=True)

# prepare server
app = Flask(__name__)
app.secret_key = b'effer234\n\xec]/'
Bootstrap(app)

socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

SID_TO_STREAMED_FILES: Dict[str, Reader] = {}  # files that are streamed through socket


@app.route("/")
def index():
    solution_names = []
    for dirname in os.listdir(os.path.join(ADEPL_DIR, "console_writer")):
        if dirname.startswith("."):
            continue

        solution_names.append(dirname)

    return render_template("index.html", solution_names=solution_names)


@app.route("/solution/<solution_name>")
def show_solution(solution_name):
    executor_names = []
    for dirname in os.listdir(os.path.join(ADEPL_DIR, "console_writer", solution_name)):
        if dirname.startswith("."):
            continue

        executor_names.append(dirname)

    executor_names.sort()

    return render_template("solution.html", solution_name=solution_name, executor_names=executor_names)


@app.route("/console/<solution_name>/<executor_name>")
def console(solution_name, executor_name):
    return render_template("console.html", solution_name=solution_name, executor_name=executor_name)


@socketio.on('disconnect')
def client_disconnected():
    sid = request.sid
    if sid in SID_TO_STREAMED_FILES:
        SID_TO_STREAMED_FILES[sid].close()
        SID_TO_STREAMED_FILES[sid] = None


@socketio.on('subscribe_console')
def client_connected(json):
    solution_name = json["solution_name"]
    executor_name = json["executor_name"]

    file_path = os.path.join(ADEPL_DIR, "console_writer", solution_name, executor_name, "console.txt")

    reader = Reader(file_path)
    sid = request.sid

    if sid in SID_TO_STREAMED_FILES:
        SID_TO_STREAMED_FILES[sid].close()

    SID_TO_STREAMED_FILES[sid] = reader

    def send_data(data: bytes):
        socketio.emit("console_data", {"text": data.decode('utf8')}, room=sid)

    reader.subscribe(send_data)


if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=HTTP_PORT, use_reloader=False, debug=True)
