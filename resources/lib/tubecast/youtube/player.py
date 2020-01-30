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

    def play_from_youtube(self, url):  # type: (str) -> None
        self.from_yt = True
        self.play(url)

    @property
    def status_code(self):  # type: () -> int
        # TODO add more states
        return STATUS_PAUSED if xbmc.getCondVisibility('Player.Paused') else STATUS_PLAYING

    @property
    def playing(self):  # type: () -> bool
        """Whether the player is currently playing.

        This is different from `isPlaying` in that it returns `False` if the
        player is paused or otherwise not actively playing.
        """
        return xbmc.getCondVisibility("Player.Playing")

    def __should_report(self):  # type: () -> bool
        return self.cast.has_client and self.from_yt

    def __report_state_change(self):
        if not self.__should_report():
            return

        self.cast.report_state_change(self.status_code, int(self.getTime()), int(self.getTotalTime()))

    def onPlayBackStarted(self):
        if not self.__should_report():
            return

        try:
            playing_time = int(self.getTime())
        except Exception:
            playing_time = 0

        self.cast.report_playback_started(playing_time)

        while self.isPlaying() and self.__should_report() and not monitor.abortRequested():
            self.__report_state_change()
            monitor.waitForAbort(5)

    def onPlayBackResumed(self):
        self.__report_state_change()

    def onPlayBackPaused(self):
        self.__report_state_change()

    def onPlayBackEnded(self):
        if self.__should_report():
            self.cast.report_playback_ended()

        self.from_yt = False

    def onPlayBackSeek(self, time, seek_offset):
        self.__report_state_change()

    def onPlayBackStopped(self):
        # FIXME: This should probably behave differently than when the video ends naturally...
        if self.cast.has_client:
            self.onPlayBackEnded()
