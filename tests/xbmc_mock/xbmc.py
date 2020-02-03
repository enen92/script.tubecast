import logging

from mock import Mock

LOGFATAL = logging.CRITICAL
LOGERROR = logging.ERROR
LOGWARNING = logging.WARNING
LOGINFO = logging.INFO
LOGDEBUG = logging.DEBUG
LOGNONE = logging.NOTSET


def log(msg, level=LOGDEBUG):
    logging.log(level, msg)


executeJSONRPC = Mock()

getInfoLabel = Mock()
getCondVisibility = Mock()

_MONITOR = None


class Monitor(object):
    def __new__(cls, *args, **kwargs):
        global _MONITOR
        if _MONITOR is None:
            _MONITOR = super(Monitor, cls).__new__(cls, *args, **kwargs)
        return _MONITOR

    _abort_requested = False
    _notifications = []

    def abortRequested(self):
        return self._abort_requested

    def waitForAbort(self, timeout=-1):
        raise NotImplementedError
        return self._abort_requested

    def onNotification(self, sender, method, data):
        self._notifications.append((sender, method, data))
