# -*- coding: utf-8 -*-
import xbmc

from resources.lib.kodi.utils import get_setting_as_bool
from resources.lib.tubecast.chromecast import Chromecast
from resources.lib.tubecast.kodicast import Kodicast, generate_uuid
from resources.lib.tubecast.ssdp import SSDPserver
from resources.lib.kodi import kodilogging

logger = kodilogging.get_logger("service")
monitor = xbmc.Monitor()


def run():
    generate_uuid()

    # Start HTTP server
    chromecast = Chromecast(monitor)
    chromecast_addr = chromecast.start()

    # Start SSDP service
    ssdp_server = None
    if get_setting_as_bool('enable-ssdp'):
        try:
            ssdp_server = SSDPserver()
            ssdp_server.start(chromecast_addr, interfaces=Kodicast.interfaces)
        except Exception as e:
            logger.error("Error initializing SSDP server: {}".format(str(e)))

    while not monitor.abortRequested():
        monitor.waitForAbort(1)

    # Abort services
    if ssdp_server is not None and get_setting_as_bool('enable-ssdp'):
        try:
            ssdp_server.shutdown()
        except Exception as e:
            logger.error("Error shutting down SSDP server: {}".format(str(e)))
    
    try:
        chromecast.abort()
    except Exception as e:
        logger.error("Error shutting down Chromecast server: {}".format(str(e)))
