import time
import schedule
import sys

from common import screenshot
from common.adb import Adb

APP_MAIN = "com.facishare.fs/com.facishare.fs.biz_function.subbiz_attendance_new.AttendanceActivity"


def schedule_job():
    adb = Adb()

    # 手机屏幕唤醒
    state = adb.run("shell dumpsys window policy")
    if 'mShowingLockscreen=true' in state:
        if 'mScreenOnFully=false' in state:
            adb.run('shell input keyevent 26')
        adb.run('shell input swipe 540 1200 540 100 800')

    # 启动应用
    window_info = adb.run("shell dumpsys window|grep mCurrentFocus")
    if APP_MAIN not in window_info:
        adb.run("shell am start -n {}".format(APP_MAIN))

    # 截图, 进行判断
    time.sleep(5)
    screenshot.check_screenshot()

    # 签到
    adb.run("shell input swipe 200 1722 800 1722 1000")

    # 截图,判断
    time.sleep(5)
    screenshot.pull_screenshot()

    # 应用退出
    adb.run("shell am force-stop com.facishare.fs")
    # adb.run("shell pm clear com.facishare.fs") // 清除所有的数据


def execute():
    try:
        schedule.every().day.at("08:05").do(schedule_job)
        schedule.every().day.at("19:10").do(schedule_job)

        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        sys.exit(1)


if __name__ == '__main__':
    execute()
