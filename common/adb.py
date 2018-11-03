import os
import subprocess

import re

"""
针对Linux操作系统
"""


class Adb(object):
    def __init__(self, adb_path='adb'):
        try:
            subprocess.Popen([adb_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.adb_path = adb_path
        except OSError:
            try:
                subprocess.Popen([adb_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except OSError:
                pass
            print('请安装 ADB 及驱动并配置环境变量')
            exit(1)

    def get_screen(self):
        """
        返回屏幕的 width 和 height
        """
        process = os.popen(self.adb_path + ' shell wm size')
        output = process.read()
        m = re.search(r'(\d+)x(\d+)', output)
        if m:
            return m.group(1), m.group(2)
        return 1080, 1920

    def get_device_info(self) -> dict:
        """
        返回设备的信息
        """
        command = """
        {adb} shell getprop ro.boot.serialno && \\
        {adb} shell getprop ro.build.version.release && \\
        {adb} shell getprop ro.build.version.sdk && \\
        {adb} shell getprop ro.product.brand && \\
        {adb} shell getprop ro.product.model
        """.format(adb=self.adb_path)
        process = os.popen(command)
        output = process.read()
        info = str(output).split("\n")
        return {
            'serialno': info[0],
            'release': info[1],
            'sdk': info[2],
            'brand': info[3],
            'model': info[4]
        }

    def run(self, raw_command):
        command = '{} {}'.format(self.adb_path, raw_command)
        process = os.popen(command)
        output = process.read()
        return output

    def get_density(self):
        process = os.popen(self.adb_path + ' shell wm density')
        output = process.read()
        return output

    def adb_path(self):
        return self.adb_path

    def test_device(self):
        print('检查设备是否连接...')
        command_list = [self.adb_path, 'devices']
        process = subprocess.Popen(command_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = process.communicate()
        if output[0].decode('utf8') == 'List of devices attached\n\n':
            print('未找到设备')
            print('adb 输出:')
            for each in output:
                print(each.decode('utf8'))
            exit(1)
        print('设备已连接')
        print('adb 输出:')
        for each in output:
            print(each.decode('utf8'))
