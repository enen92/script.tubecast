# -*- coding: utf-8 -*-
from resources.lib.kodi import kodilogging

import xbmc

monitor = xbmc.Monitor()

STATUS_PLAYING = 1
STATUS_PAUSED = 2
STATUS_LOADING = 3
STATUS_STOPPED = 4


class CastPlayer(xbmc.Player):
    def __init__(self, cast):  # type: (YoutubeCastV1) -> None
        super(CastPlayer, self).__init__()
        self.cast = cast
        # auxiliary variable to know if the request came from the youtube background thread
        self.from_yt = False
        self.playing = False

    def play_from_youtube(self, url):  # type: (str) -> None
        self.from_yt = True
        self.play(url)

    @property
    def status_code(self):  # type: () -> int
        # TODO add more states
        return STATUS_PAUSED if xbmc.getCondVisibility('Player.Paused') else STATUS_PLAYING

    def _should_report(self):  # type: () -> bool
        return self.cast.has_client and self.from_yt

    def __report_state_change(self):
        self.cast.report_state_change(self.status_code, int(self.getTime()), int(self.getTotalTime()))

    def onPlayBackStarted(self):
        self.playing = True

        if not self._should_report():
            return

        try:
            playing_time = int(self.getTime())
        except Exception:
            playing_time = 0

        self.cast.report_playback_started(playing_time)

        while self.isPlaying() and self._should_report() and not monitor.abortRequested():
            self.__report_state_change()
            monitor.waitForAbort(5)

    def onPlayBackResumed(self):
        self.playing = True
        if self._should_report():
            self.__report_state_change()

    def onPlayBackPaused(self):
        self.playing = False
        if self._should_report():
            self.__report_state_change()

    def onPlayBackEnded(self):
        self.playing = False
        if self._should_report():
            self.cast.report_playback_ended()

        self.from_yt = False

    def onPlayBackSeek(self, time, seek_offset):
        if self._should_report():
            self.__report_state_change()

    def onPlayBackStopped(self):
        if self.cast.has_client:
            self.onPlayBackEnded()
