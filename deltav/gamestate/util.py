
import time


class DebugClock(object):

    def __init__(self, running_avg_size = 100):
        self._times = []
        self.max = 0
        self._t1 = None
        self._running_avg_size = running_avg_size

    def start_timer(self):
        self._t1 = time.time()

    def record_time(self):
        if self._t1:
            t = time.time() - self._t1
            self.add(t)
            return t
        return 0

    def clear_timer(self):
        self._t1 = None

    def add(self, t):
        self._times.append(t)
        if t > self.max:
            self.max = t
        if len(self._times) > self._running_avg_size:
            self._times = self._times[-self._running_avg_size:]

    @property
    def avg(self):
        if self._times:
            return sum(self._times)/len(self._times)
        else:
            return 0

    @property
    def latest(self):
        try:
            return self._times[-1]
        except IndexError:
            return 0