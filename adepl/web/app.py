import os
from typing import Dict

from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO

from adepl import ADEPL_RUNTIME_DIR
from adepl.feature_modules.console_writer import ConsoleWriter
from adepl.utils import list_dir_objects
from adepl.utils.rotary_files.reader import Reader

HTTP_PORT = 7895
MAX_HISTORY_LENGTH = 1000

# run env initialization
os.makedirs(ADEPL_RUNTIME_DIR, exist_ok=True)
SID_TO_STREAMED_FILES: Dict[str, Reader] = {}  # files that are streamed through socket

# prepare server
app = Flask(__name__)
app.secret_key = b'effer234\n\xec]/'
Bootstrap(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

@app.route("/")
def index():
    solution_names = list_dir_objects(ADEPL_RUNTIME_DIR)
    return render_template("index.html", solution_names=solution_names)


@app.route("/solution/<solution_name>")
def show_solution(solution_name):
    executor_names = list_dir_objects(os.path.join(ADEPL_RUNTIME_DIR, solution_name))
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

    reader = ConsoleWriter.create_reader(solution_name, executor_name)

    sid = request.sid
    if sid in SID_TO_STREAMED_FILES:
        SID_TO_STREAMED_FILES[sid].close()

    SID_TO_STREAMED_FILES[sid] = reader

    def send_data(data: bytes):
        socketio.emit("console_data", {"text": data.decode('utf8')}, room=sid)

    reader.subscribe(send_data)


if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=HTTP_PORT, use_reloader=False, debug=True)
