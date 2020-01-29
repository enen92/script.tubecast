# -*- coding: utf-8 -*-
import json
import threading

import xbmc

from resources.lib.tubecast.youtube import kodibrigde


class VolumeMonitor(xbmc.Monitor):

    def __init__(self, cast):
        super(VolumeMonitor, self).__init__()
        self.cast = cast
        self.kodi_volume = kodibrigde.get_kodi_volume()

        self.thread = None

    def onNotification(self, sender, method, data):
        if self.cast.has_client and method == "Application.OnVolumeChanged":
            new_volume = json.loads(data)["volume"]
            if self.kodi_volume != new_volume:
                self.kodi_volume = new_volume
                self.youtubecastv1.set_volume(new_volume)
