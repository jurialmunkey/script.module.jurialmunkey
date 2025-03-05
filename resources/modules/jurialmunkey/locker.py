import xbmc
import xbmcvfs
from jurialmunkey.tmdate import get_timestamp, set_timestamp


class MutexFileLock():
    def __init__(self, lockfile, timeout=10, polling=0.01, kodi_log=None):
        """ ContextManager for mutex lock """
        self._timeout = timeout
        self._polling = polling
        self._lockfile = lockfile
        self._kodi_log = kodi_log
        self.aquire_lock()

    @property
    def monitor(self):
        try:
            return self._monitor
        except AttributeError:
            self._monitor = xbmc.Monitor()
            return self._monitor

    @property
    def kodi_log(self):
        try:
            return self._kodi_log
        except AttributeError:
            from jurialmunkey.logger import Logger
            self._kodi_log = Logger('[script.module.jurialmunkey]\n')
            return self._kodi_log

    @property
    def time_exp(self):
        try:
            return self._time_exp
        except AttributeError:
            self._time_exp = set_timestamp(self._timeout)
            return self._time_exp

    def lock_exists(self):
        if xbmcvfs.exists(self._lockfile):
            return self._lockfile

    def create_lock(self):
        if self.lock_exists():
            return
        with xbmcvfs.File(self._lockfile, 'w') as f:
            f.write('locked')
        return self._lockfile

    def delete_lock(self):
        if not self.lock_exists():
            return
        xbmcvfs.delete(self._lockfile)

    def aquire_lock(self):
        # Aquire lock if available
        if self.create_lock():
            return

        # Early exit: System abort
        if self.monitor.abortRequested():
            return

        # Early exit: Timed out while waiting
        if not get_timestamp(self.time_exp):
            self.kodi_log(f'{self._lockfile} Timeout!', 1)
            return

        # Wait in loop
        self.monitor.waitForAbort(self._polling)
        return self.aquire_lock()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.delete_lock()
