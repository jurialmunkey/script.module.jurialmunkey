import xbmc
from xbmcaddon import Addon as KodiAddon


class KodiPlugin():
    def __init__(self, addon_id):
        self._addon_id = addon_id
        self._addon = KodiAddon(addon_id)
        self._addon_name = self._addon.getAddonInfo('name')
        self._addon_path = self._addon.getAddonInfo('path')

    @property
    def settings(self):
        return self._addon.getSettings()

    def get_setting(self, setting, mode='bool'):
        def get_func():
            if mode == 'bool':
                return self.settings.getBool
            if mode == 'int':
                return self.settings.getInt
            if mode == 'str':
                return self.settings.getString
        return get_func()(setting)

    def set_setting(self, setting, data, mode='bool'):
        def set_func():
            if mode == 'bool':
                return self.settings.setBool
            if mode == 'int':
                return self.settings.setInt
            if mode == 'str':
                return self.settings.setString
        return set_func()(setting, data)

    def get_localized(self, localize_int=0):
        if localize_int < 30000 or localize_int >= 33000:
            return xbmc.getLocalizedString(localize_int)
        return self._addon.getLocalizedString(localize_int)


def format_name(cache_name, *args, **kwargs):
    # Define a type whitelist to avoiding adding non-basic types like classes to cache name
    permitted_types = (int, float, str, bool, bytes)
    for arg in args:
        if not isinstance(arg, permitted_types):
            continue
        cache_name = f'{cache_name}/{arg}' if cache_name else f'{arg}'
    for key, value in sorted(kwargs.items()):
        if not isinstance(value, permitted_types):
            continue
        cache_name = f'{cache_name}&{key}={value}' if cache_name else f'{key}={value}'
    return cache_name


def format_folderpath(path, content='videos', affix='return', info=None, play='PlayMedia'):
    if not path:
        return
    if info == 'play':
        return f'{play}({path})'
    if xbmc.getCondVisibility("Window.IsMedia") and xbmc.getInfoLabel("System.CurrentWindow").lower() == content:
        return f'Container.Update({path})'
    return f'ActivateWindow({content},{path},{affix})'


def set_kwargattr(obj, kwargs):
    for k, v in kwargs.items():
        setattr(obj, k, v)
