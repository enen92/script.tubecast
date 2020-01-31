# -*- coding: utf-8 -*-
import errno

import xbmc

from resources.lib.kodi import kodilogging, utils
from resources.lib.kodi.utils import get_setting_as_bool
from resources.lib.tubecast.chromecast import Chromecast
from resources.lib.tubecast.kodicast import Kodicast, generate_uuid
from resources.lib.tubecast.ssdp import SSDPserver

logger = kodilogging.get_logger()
monitor = xbmc.Monitor()


def run():
    generate_uuid()

    # Start HTTP server
    chromecast = Chromecast(monitor)
    chromecast_addr = chromecast.start()

    # Start SSDP service
    if get_setting_as_bool('enable-ssdp'):
        ssdp_server = SSDPserver()
        try:
            ssdp_server.start(chromecast_addr, interfaces=Kodicast.interfaces)
        except IOError as e:
            if e.errno == errno.ENODEV:
                logger.warning("Failed to start SSDP server most likely due to network issues. "
                               "Please make sure you're connected to the internet and then try again.")
                utils.notification(message=utils.get_string(32014))
            else:
                logger.exception("failed to add membership")

    while not monitor.abortRequested():
        monitor.waitForAbort(1)

    # Abort services
    if get_setting_as_bool('enable-ssdp'):
        ssdp_server.shutdown()
    chromecast.abort()
