import os

import eventlet

eventlet.monkey_patch()

from flask import Flask, render_template, make_response
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

socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")


@app.route("/console/<solution_name>/<producer_name>")
def console(solution_name, producer_name):
    file_path = os.path.join(ADEPL_DIR, "console_writer", solution_name, producer_name, "console.txt")

    with open(file_path, "r") as f:
        r = make_response("".join(f.readlines()[-200:]))
        r.cache_control.no_cache = True
        r.headers.set("Content-Type", "text/plain")
        return r


if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=HTTP_PORT, use_reloader=False, debug=True)
