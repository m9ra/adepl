import os
import signal
import subprocess
from queue import Queue
from threading import Thread, RLock, Event


class ProcessProxy(object):
    def start(self, cmd, cwd=None, stdout=None, stderr=None, env=None):
        self._p = subprocess.Popen(cmd, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   preexec_fn=os.setsid, env=env)
        self._stdout = stdout
        self._stderr = stderr
        self._queue = Queue()
        self._closed_pipe_count = 0
        self._finish_event = Event()
        self._start_pipe_thread(self._p.stdout)
        self._start_pipe_thread(self._p.stderr)
        Thread(target=self._process_reader, daemon=True).start()

    def wait(self):
        self._finish_event.wait()

    def kill(self):
        if self._p is None:
            return

        os.killpg(self._p.pid, signal.SIGKILL)
        self.wait()

    def _process_error_line(self, line):
        if self._stderr:
            self._stderr(line)

    def _process_output_line(self, line):
        if self._stdout:
            self._stdout(line)

    def _process_reader(self):
        while self._closed_pipe_count < 2:
            # wait until stderr and stdout are exhausted

            pipe, line = self._queue.get()

            if line is None:
                self._closed_pipe_count += 1
                continue

            is_err = pipe == self._p.stderr
            if is_err:
                self._process_error_line(line)
            else:
                self._process_output_line(line)

        self._process_error_line(None)
        self._process_output_line(None)
        self._p.wait()
        self._p = None
        self._finish_event.set()

        return None

    def _get_line(self, pipe):
        line = pipe.readline().decode()
        if line is '':
            return None

        if line.endswith('\n'):
            line = line[:-1]

        return line

    def _reader(self, pipe):
        try:
            with pipe:
                while True:
                    line = self._get_line(pipe)
                    if line is None:
                        break

                    self._queue.put((pipe, line))

        finally:
            self._queue.put((pipe, None))

    def _start_pipe_thread(self, pipe):
        th = Thread(target=self._reader, args=[pipe])
        th.daemon = True
        th.start()
