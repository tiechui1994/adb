from common.adb import Adb
from common.env import ENV


class Screen(object):
    adb = Adb()

    @classmethod
    def lock_screen(cls):
        """
        锁定屏幕
        """
        info = cls.adb.run("shell dumpsys window policy")
        if "mShowingLockscreen=true" in info:
            if "mScreenOnFully=false" in info:
                # 锁定且屏幕为暗
                return
            else:
                # 锁定屏幕为亮
                cls.adb.run(" shell input keyevent 82")
        else:
            cls.adb.run(" shell input keyevent 26")

    @classmethod
    def unlock_screen(cls, password=None):
        """
        屏幕解锁
        """
        # 360*1230
        info = cls.adb.run("shell dumpsys window policy")
        if "mShowingLockscreen=true" in info:
            if "mScreenOnFully=false" in info:
                cls.adb.run("shell input keyevent 26")

            # 滑动
            cls.adb.run("shell input swipe {x1} {y1} {x2} {y2} {time}".format(
                x1=360, y1=1230,
                x2=360, y2=600,
                time=300
            ))

            # 查询当前状态
            info = cls.adb.run("shell dumpsys window policy")
            if "mShowingLockscreen=false" in info:
                return True

            if password is None:
                return False

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
                points = cls._get_ten_points(point1.get('x'), point1.get('y'), point2.get('x'), point2.get('y'))

                if len(points) == 0:
                    return False
                for point in points:
                    command += cls._click(point[0], point[1])
            command += cls._end()
            print(command)

            # 查询当前状态
            info = cls.adb.run("shell dumpsys window policy")
            if "mShowingLockscreen=false" in info:
                return True
            else:
                return False

    @staticmethod
    def _start():
        # EN_KEY BTN_TOUCH DOWN
        # EN_KEY BTN_TOOL_FINGER DOWN  手指触摸
        # EV_ABS ABS_MT_TRACKING_ID 0  追踪唯一id

        template = """
adb shell sendevent {DEVICE} {EN_KEY} {BTN_TOUCH} {DOWN} && \\
adb shell sendevent {DEVICE} {EN_KEY} {BTN_TOOL_FINGER} {DOWN} && \\
adb shell sendevent {DEVICE} {EV_ABS} {ABS_MT_TRACKING_ID} 0 && \\
""".format(**ENV)
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
adb shell sendevent {DEVICE} {EV_SYN} {BTN_TOOL_FINGER} {UP} && \\
adb shell sendevent {DEVICE} {EV_SYN} {SYN_REPORT} 0
        """.format(**ENV)

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
adb shell sendevent {DEVICE} {EV_SYN} {BTN_TOOL_FINGER} {p} && \\
adb shell sendevent {DEVICE} {EV_SYN} {SYN_REPORT} 0 && \\
"""
        return template.format(x=x, y=y, m=6, p=6, **ENV)

    @staticmethod
    def _get_ten_points(x1, y1, x2, y2):
        points = []
        if x1 == x2 and y1 == y2:
            return points

        if x1 == x2:
            for i in range(2, 12, 2):
                points.append((x1, y1 + (y2 - y1) / 20 * i))
            return points

        if y1 == y2:
            for i in range(1, 20, 2):
                points.append((x1 + (x2 - x1) / 20 * i, y1))
            return points

        step = (x2 - x1) / 20
        k = (y2 - y1) / (x2 - x1)
        b = y1 - k * x1
        for i in range(1, 20, 2):
            x = x1 + i * step
            y = k * x + b
            points.append((x, y))

        return points


if __name__ == '__main__':
    Screen.unlock_screen("3586")
