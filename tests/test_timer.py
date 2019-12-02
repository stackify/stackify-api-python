import time
from unittest import TestCase
try:
    from unittest import mock
except Exception:
    import mock

from stackify.timer import RepeatedTimer


class TimerTest(TestCase):
    def setUp(self):
        self.function_mock = mock.Mock()
        self.timer = RepeatedTimer(0.1, self.function_mock)
        self.timer.start()

    def shutDown(self):
        self.timer.stop()

    def test_start(self):
        assert self.timer._started

    def test_stop(self):
        self.timer.stop()

        assert not self.timer._started

    def test_timer(self):
        time.sleep(0.3)

        assert self.function_mock.called
        assert self.function_mock.call_count >= 2
