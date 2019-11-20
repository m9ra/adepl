import os
from threading import Thread
from time import sleep

from flask import Flask, render_template, make_response, request
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO

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


@socketio.on('subscribe_console')
def client_connected(json):
    solution_name = json["solution_name"]
    executor_name = json["executor_name"]

    file_path = os.path.join(ADEPL_DIR, "console_writer", solution_name, executor_name, "console.txt")
    stream_file(file_path, request.sid)


def stream_file(file_path, sid):
    # todo move to some utility class
    def _stream_file():
        # todo use some more reasonable eventing - reopening files is ugly, but it solves file recreation
        with open(file_path, "r", buffering=1) as f:
            # seek somewhere close to file end
            f.seek(0, os.SEEK_END)
            f.seek(max(0, f.tell() - 5000), os.SEEK_SET)  # this hack is needed due to text read mode
            f.readline()  # align to next line start
            current_position = f.tell()

        while True:
            with open(file_path, "r", buffering=1, encoding="utf8") as f:
                f.seek(0, os.SEEK_END)

                if f.tell() < current_position:
                    socketio.emit("console_reset", {}, room=sid)
                    current_position = 0
                    continue

                f.seek(current_position, os.SEEK_SET)

                next_data = f.read()
                current_position = f.tell()

                if next_data:
                    socketio.emit("console_data", {"text": next_data}, room=sid)

                sleep(0.5)

    th = Thread(target=_stream_file)
    th.daemon = True
    th.start()


if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=HTTP_PORT, use_reloader=False, debug=True)
