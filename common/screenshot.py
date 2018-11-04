"""
手机屏幕截图的代码
"""
import subprocess
import os
import sys
from PIL import Image
from io import StringIO
from common.adb import Adb

__all__ = ['pull_screenshot']

adb = Adb()
# SCREENSHOT_WAY 是截图方法，经过 check_screenshot 后,会自动递减, 不需手动修改
SCREENSHOT_WAY = 3


def pull_screenshot(picturepath='./autojump.png') -> Image:
    """
    :exception: IOError
    :return: Image
    """
    if SCREENSHOT_WAY == 3:
        return _check_screenshot(picturepath)
    else:
        return _pull_screenshot(picturepath)


def _pull_screenshot(picturepath):
    """
    获取屏幕截图，目前有 0 1 2 3 四种方法，未来添加新的平台监测方法时，
    可根据效率及适用性由高到低排序
    """
    global SCREENSHOT_WAY
    if 1 <= SCREENSHOT_WAY <= 3:
        process = subprocess.Popen(
            adb.adb_path + ' shell screencap -p',
            shell=True, stdout=subprocess.PIPE)
        binary_screenshot = process.stdout.read()
        if SCREENSHOT_WAY == 2:
            binary_screenshot = binary_screenshot.replace(b'\r\n', b'\n')
        elif SCREENSHOT_WAY == 1:
            binary_screenshot = binary_screenshot.replace(b'\r\r\n', b'\n')
        return Image.open(StringIO(binary_screenshot))
    elif SCREENSHOT_WAY == 0:
        _, filename = os.path.split(picturepath)
        adb.run('shell screencap -p /sdcard/{filename}'.format(filename=filename))
        adb.run('pull /sdcard/{filename} {path}'.format(filename=picturepath, path=picturepath))
        return Image.open('{path}'.format(path=picturepath))


def _check_screenshot(picturepath):
    """
    检查获取截图的方式
    """
    global SCREENSHOT_WAY
    if os.path.isfile(picturepath):
        try:
            os.remove(picturepath)
        except Exception:
            pass
    if SCREENSHOT_WAY < 0:
        print('暂不支持当前设备')
        sys.exit()
    try:
        im = _pull_screenshot(picturepath)
        im.load()
        im.close()
        return im
    except Exception:
        SCREENSHOT_WAY -= 1
        return _check_screenshot(picturepath)
