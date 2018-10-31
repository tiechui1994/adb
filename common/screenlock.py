from common.adb import Adb

adb = Adb()


def lock_screen():
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


def unlock_screen(password=None):
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

        # 查询当前状态
        info = adb.run("shell dumpsys window policy")
        if "mShowingLockscreen=false" in info:
            return True

        if password is None:
            return False

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
        for i in range(1, length):
            point1 = table_password[password[i - 1]]
            point2 = table_password[password[i]]
            adb.run("shell input swipe {x1} {y1} {x2} {y2}".format(
                x1=point1.get('x'), y1=point1.get('y'),
                x2=point2.get('x'), y2=point2.get('y'),
            ))
