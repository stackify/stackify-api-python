import time
from threading import Event, Thread


class RepeatedTimer(object):
    '''
    Repeater class that call the function every interval seconds.
    '''

    def __init__(self, interval, function, *args, **kwargs):
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.started = time.time()
        self.event = Event()
        self.thread = Thread(target=self._target)
        self._started = False

    def _target(self):
        while not self.event.wait(self._time):
            self.function(*self.args, **self.kwargs)

    @property
    def _time(self):
        return self.interval - ((time.time() - self.started) % self.interval)

    def start(self):
        if not self._started:
            self._started = True
            self.thread.setDaemon(True)
            self.thread.start()

    def stop(self):
        if self._started:
            self._started = False
            self.event.set()
            self.thread.join()
