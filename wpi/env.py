import logging
import os
import platform
import sys

from wpi import load_module
from wpi.user_sample import config_, ps_

bundle_data_folder = '_data'

Z7_FOLDER = '7z'
Z7_EXE = '7z.exe'
Z7_DLL = '7z.dll'


def get_ps__filename():
    from wpi.user_sample import ps_

    return os.path.splitext(os.path.split(ps_.__file__)[1])[0] + '.py'


def get_config__filename():
    from wpi.user_sample import config_

    return os.path.splitext(os.path.split(config_.__file__)[1][0] + '.py')


def_config_filename = 'config.py'

def_ps_filename = '_.py'

def_drivers_dirname = 'drivers'

user_wpi_dir = os.path.join(os.getenv('LOCALAPPDATA'), 'wpi')
user_config_sample_path = os.path.join(user_wpi_dir, 'config_.py')
user_config_path = os.path.join(user_wpi_dir, def_config_filename)

user_logs_dir = os.path.join(os.getenv('LOCALAPPDATA'), 'wpi_logs')


def is_exe():
    if getattr(sys, 'frozen', False) is not False:
        return True
    else:
        return False


def meipass_path():
    return getattr(sys, '_MEIPASS')


def exe_path():
    if is_exe():
        return sys.executable
    elif __file__:
        return __file__


def exe_dir():
    return os.path.dirname(exe_path())


def find_7z_in_reg():
    regkeys = (r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall',
               r'HKEY_LOCAL_MACHINE\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall')

    from wpi.reg import Node

    b32_location = None
    b64_location = None

    for one in regkeys:
        n = Node(one)
        for k, sub in n.items():
            if k == '7-Zip':
                if sub.tips['DisplayName'].endswith('(x64)'):
                    b64_location = sub.tips['InstallLocation']
                else:
                    b32_location = sub.tips['InstallLocation']

    return b32_location, b64_location


def path_of_7z():
    if is_exe():
        z7_path = os.path.join(meipass_path(), bundle_data_folder, Z7_EXE)
        if os.path.isfile(z7_path):
            return z7_path

    b32_dir, b64_dir = find_7z_in_reg()

    if b32_dir and os.path.isfile(os.path.join(b32_dir, Z7_EXE)):
        return os.path.isfile(os.path.join(b32_dir, Z7_EXE))

    elif b64_dir and os.path.isfile(os.path.join(b64_dir, Z7_EXE)):
        return os.path.isfile(os.path.join(b64_dir, Z7_EXE))

    else:
        logging.warning('7-Zip cannot be found.')
        return None


def bundle_files():
    return (
        path_of_7z(),
        os.path.join(os.path.split(path_of_7z())[0], Z7_DLL),
        config_.__file__,
        ps_.__file__,
    )


class Config:
    __slots__ = ['z7_path', 'drivers_dir', 'archive_exts']

    def __init__(self, obj=None):
        for k in self.__slots__:
            setattr(self, k, getattr(obj, k, None))


def load_config(path):
    return Config(load_module(path))


def supply_config(config=None):
    c = Config(config)

    c.z7_path = c.z7_path or path_of_7z()

    c.archive_exts = c.archive_exts or ['.zip', '.7z', '.rar', '.exe']

    return c


CUR_OS = platform.release().lower()
ALL_OS = {'xp', '7', '10'} | {CUR_OS}

B32 = '32'
B64 = '64'
ALL_BITS = {'32', '64'}

if platform.machine().endswith('64'):
    CUR_BIT = '64'
elif platform.machine().endswith('86'):
    CUR_BIT = '32'
else:
    raise Exception


PYTHON_BIT = platform.architecture()[0][0:2]
