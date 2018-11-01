"""
调取配置文件和屏幕分辨率的代码
"""
import os
import sys
import json
import re
from common.adb import Adb


adb = Adb()


def open_accordant_config():
    """
    调用配置文件
    """
    width, height = adb.get_screen()
    screen_size = "{width}x{height}".format(height=height, width=width)
    config_file = "{path}/config/{screen_size}/config.json".format(
        path=sys.path[0],
        screen_size=screen_size
    )

    # 优先获取执行文件目录的配置文件
    here = sys.path[0]
    for file in os.listdir(here):
        if re.match(r'(.+)\.json', file):
            file_name = os.path.join(here, file)
            with open(file_name, 'r') as f:
                print("Load config file from {}".format(file_name))
                return json.load(f)

    # 根据分辨率查找配置文件
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            print("正在从 {} 加载配置文件".format(config_file))
            return json.load(f)
    else:
        with open('{}/config/default.json'.format(sys.path[0]), 'r') as f:
            print("Load default config")
            return json.load(f)
