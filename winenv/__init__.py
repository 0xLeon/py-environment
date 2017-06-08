"""Provides function to edit environment variables in python"""

from __future__ import unicode_literals
from __future__ import absolute_import
from builtins import str as text
import os
import ctypes

try:
    import winreg
except ImportError:
    import _winreg as winreg

__version__ = '0.0.0'

ENV_USER = 0x00
ENV_SYSTEM = 0x02

def get_env_var(name, env=ENV_SYSTEM):
    """Gets an environment variable from the registry"""

    key = _get_reg_key(env)

    try:
        return winreg.QueryValueEx(key, name)[0]
    except WindowsError:
        return None
    finally:
        winreg.CloseKey(key)

def set_env_var(name, value, regtype=winreg.REG_SZ, overwrite=True, env=ENV_SYSTEM):
    """Add new or overwrite existing environment variables"""

    if not name or len(name) < 1:
        raise ValueError("Invalid name value")

    if not value or len(value) < 1:
        raise ValueError("Invalid value")

    if regtype != winreg.REG_SZ and regtype != winreg.REG_EXPAND_SZ:
        raise ValueError("Invalid type")

    key = _get_reg_key(env, winreg.KEY_ALL_ACCESS)
    cval = None
    ctype = regtype

    try:
        cval, ctype = winreg.QueryValueEx(key, name)
    except WindowsError:
        pass

    if cval is None or overwrite:
        winreg.SetValueEx(key, name, 0, ctype, value)
        notify_env_change()

        if regtype == winreg.REG_EXPAND_SZ:
            os.environ[name] = text(winreg.ExpandEnvironmentStrings(value))
        else:
            os.environ[name] = text(value)

        winreg.CloseKey(key)
    else:
        winreg.CloseKey(key)
        raise EnvironmentError('Environment variable {} already exists, but overwrite is false'.format(name))

def append_env_var(name, avalue, prepend=False, separator=';', env=ENV_SYSTEM):
    """Appends a value to a string separated list value"""

    if not name or len(name) < 1:
        raise ValueError("Invalid name value")

    if not avalue or len(avalue) < 1:
        raise ValueError("Invalid new list item")

    if not separator or len(separator) < 1:
        raise ValueError("Invalid separator")

    key = _get_reg_key(env, winreg.KEY_ALL_ACCESS)
    val = ""
    vtype = winreg.REG_EXPAND_SZ

    try:
        val, vtype = winreg.QueryValueEx(key, name)
    except WindowsError:
        pass

    if not val:
        if prepend:
            val = avalue + separator + val
        else:
            if val[-1] != separator:
                val = val + separator

            val = val + avalue
    else:
        val = avalue

    winreg.SetValueEx(key, name, 0, vtype, val)
    notify_env_change()
    winreg.CloseKey(key)

def _get_reg_key(env=ENV_SYSTEM, access=winreg.KEY_READ):
    if env == ENV_SYSTEM:
        return winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment", 0, access)
    elif env == ENV_USER:
        return winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, access)
    else:
        raise ValueError("Invalid environment")

def notify_env_change():
    """Sends the necesarry Windows message to the system to notify the environment change"""

    # SendNotifyMessageW(HWND_BROADCAST, WM_SETTINGCHANGE, NULL, "Environment")
    ctypes.windll.user32.SendNotifyMessageW(0xffff, 0x001a, None, "Environment".encode('utf_16'))
