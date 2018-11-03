import os

from common.adb import Adb
from common.env import Env
from utils.consts import LOCKTYPE
from utils.functions import get_points

adb = Adb()


class Screen(object):
    @classmethod
    def lock_screen(cls):
        """
        锁定屏幕
        """
        info = adb.run("shell dumpsys window policy")
        if "mShowingLockscreen=true" in info:
            if "mScreenOnFully=false" in info:
                # 锁定且屏幕为暗
                return
            else:
                # 锁定屏幕为亮
                adb.run(" shell input keyevent 82")
        else:
            adb.run(" shell input keyevent 26")

    @classmethod
    def unlock_screen(cls, password=None, lock_type=LOCKTYPE.NONE):
        """
        屏幕解锁
        """
        # 360*1230
        info = adb.run("shell dumpsys window policy")
        if "mShowingLockscreen=true" in info:
            if "mScreenOnFully=false" in info:
                adb.run("shell input keyevent 26")

            # 滑动
            adb.run("shell input swipe {x1} {y1} {x2} {y2} {time}".format(
                x1=360, y1=1230,
                x2=360, y2=600,
                time=300
            ))

            # 查询当前状态(已经解锁)
            info = adb.run("shell dumpsys window policy")
            if "mShowingLockscreen=false" in info:
                return True

            # 未解锁时, lock_type 或者 password 判断
            if lock_type == LOCKTYPE.NONE or lock_type != LOCKTYPE.NONE and password is None:
                return False

            # 针对有密码的解锁
            if lock_type == LOCKTYPE.PATTERN:
                cls._unlock_screen_with_pattern(password)
            elif lock_type == LOCKTYPE.PIN:
                cls._unlock_screen_with_pin(password)

            # 再次查询当前状态
            info = adb.run("shell dumpsys window policy")
            return "mShowingLockscreen=false" in info
        else:
            return True

    @classmethod
    def _unlock_screen_with_pin(cls, password):
        pass

    @classmethod
    def _unlock_screen_with_pattern(cls, password):
        # vivo y67密码表
        table_password = {
            '1': {'x': 150, 'y': 676},
            '2': {'x': 360, 'y': 676},
            '3': {'x': 570, 'y': 676},
            '4': {'x': 150, 'y': 886},
            '5': {'x': 360, 'y': 886},
            '6': {'x': 570, 'y': 886},
            '7': {'x': 150, 'y': 1096},
            '8': {'x': 360, 'y': 1096},
            '9': {'x': 570, 'y': 1096}
        }

        length = len(password)
        command = cls._start()
        for i in range(1, length):
            point1 = table_password[password[i - 1]]
            point2 = table_password[password[i]]
            points = get_points(point1.get('x'), point1.get('y'), point2.get('x'), point2.get('y'))

            if len(points) == 0:
                return False
            for point in points:
                command += cls._click(point[0], point[1])
        command += cls._end()
        os.popen(command)

    @staticmethod
    def _start():
        # EN_KEY BTN_TOUCH DOWN
        # EN_KEY BTN_TOOL_FINGER DOWN  手指触摸
        # EV_ABS ABS_MT_TRACKING_ID 0  追踪唯一id

        template = """
adb shell sendevent {DEVICE} {EN_KEY} {BTN_TOUCH} {DOWN} && \\
adb shell sendevent {DEVICE} {EN_KEY} {BTN_TOOL_FINGER} {DOWN} && \\
adb shell sendevent {DEVICE} {EV_ABS} {ABS_MT_TRACKING_ID} 0 && \\
""".format(**Env.ENV)
        return template

    @staticmethod
    def _end():
        # EV_ABS ABS_MT_TRACKING_ID ffffffff  追踪唯一id的反数
        # EV_SYN SYN_REPORT 00000000          事件上报
        # EN_KEY BTN_TOUCH UP
        # EN_KEY BTN_TOOL_FINGER UP           手指松开
        # EV_SYN SYN_REPORT 00000000          事件上报
        template = """adb shell sendevent {DEVICE} {EV_ABS} {ABS_MT_TRACKING_ID} 4294967295 && \\
adb shell sendevent {DEVICE} {EV_SYN} {SYN_REPORT} 0 && \\
adb shell sendevent {DEVICE} {EN_KEY} {BTN_TOUCH} {UP} && \\
adb shell sendevent {DEVICE} {EN_KEY} {BTN_TOOL_FINGER} {UP} && \\
adb shell sendevent {DEVICE} {EV_SYN} {SYN_REPORT} 0
        """.format(**Env.ENV)

        return template

    @staticmethod
    def _click(x, y):
        # EV_ABS ABS_MT_POSITION_X  000001ae
        # EV_ABS ABS_MT_POSITION_Y  000001b8 #坐标
        # EV_ABS ABS_MT_TOUCH_MAJOR 6 #级别(可调)
        # EV_ABS ABS_MT_TOUCH_PRESSURE 6 #按压
        # EV_SYN SYN_REPORT 00000000 #事件上报

        template = """adb shell sendevent {DEVICE} {EV_ABS} {ABS_MT_POSITION_X} {x} && \\
adb shell sendevent {DEVICE} {EV_ABS} {ABS_MT_POSITION_Y} {y} && \\
adb shell sendevent {DEVICE} {EV_ABS} {ABS_MT_TOUCH_MAJOR} {m} && \\
adb shell sendevent {DEVICE} {EV_ABS} {BTN_TOOL_FINGER} {p} && \\
adb shell sendevent {DEVICE} {EV_SYN} {SYN_REPORT} 0 && \\
"""
        return template.format(x=x, y=y, m=6, p=6, **Env.ENV)


if __name__ == '__main__':
    Screen.unlock_screen("3586", lock_type=LOCKTYPE.PATTERN)
