from mock import Mock

_ADDON = None


class Addon(object):
    def __new__(cls, *args, **kwargs):
        global _ADDON
        if _ADDON is None:
            _ADDON = super(Addon, cls).__new__(cls, *args, **kwargs)
        return _ADDON

    getAddonInfo = Mock()

    getLocalizedString = Mock()

    getSetting = Mock()
    getSettingBool = Mock()
    getSettingInt = Mock()
    getSettingNumber = Mock()
    getSettingString = Mock()
    setSetting = Mock()
    setSettingBool = Mock()
    setSettingInt = Mock()
    setSettingNumber = Mock()
    setSettingString = Mock()

    openSettings = Mock()
