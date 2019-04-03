import json
import random
import time
import schedule
import sys
import urllib3
from datetime import date


from common import screenshot
from common.adb import Adb
from common.screenlock import Screen

APP_MAIN = "com.facishare.fs/com.facishare.fs.biz_function.subbiz_attendance_new.AttendanceActivity"
DOMAIN = "http://api.goseek.cn/Tools/holiday"
picture_path = "/home/user/Desktop/autojump.png"
manager = None
adb = None


def init():
    global manager, adb
    adb = Adb()
    manager = urllib3.PoolManager(num_pools=5)


def schedule_job():
    global adb

    # 判断
    if check_date_rest():
        return

    # 解锁
    Screen.unlock_screen()

    # 启动应用
    window_info = adb.run("shell dumpsys window|grep mCurrentFocus")
    if APP_MAIN not in window_info:
        adb.run("shell am start -n {}".format(APP_MAIN))

    # 截图, 进行判断
    random_sleep_time = random.randint(10, 1000)
    time.sleep(random_sleep_time)
    screenshot.pull_screenshot(picturepath=picture_path)

    # 签到
    adb.run("shell input swipe 200 1722 800 1722 1000")

    # 截图,判断
    time.sleep(5)
    screenshot.pull_screenshot(picturepath=picture_path)

    # 应用退出
    adb.run("shell am force-stop com.facishare.fs")
    # adb.run("shell pm clear com.facishare.fs") // 清除所有的数据


def check_date_rest():
    today = date.today()
    date_str = time.strftime('%Y%m%d', today.timetuple())
    global manager
    url = "%s?date=%s" % (DOMAIN, date_str)
    response = manager.request('GET', url)

    # 正常工作日对应结果为0, 法定节假日对应结果为1, 节假日调休补班对应的结果为2，休息日对应结果为3
    data = json.loads(str(response.data, "utf-8"))
    print("今天日期是:", time.strftime('%Y-%m-%d', today.timetuple()), "返回结果是:", data)
    if data["data"] == 0:
        return False
    elif data["data"] == 1:
        return True
    elif data["data"] == 2:
        return False
    elif data["data"] == 3:
        return True


def do():
    print(time.ctime())


def execute():
    init()
    try:
        schedule.every().day.at("08:10").do(schedule_job)
        schedule.every().day.at("20:10").do(schedule_job)

        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        sys.exit(1)


if __name__ == '__main__':
    execute()
