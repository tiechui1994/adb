"""
指令表
"""
import os
import re
from collections import OrderedDict
from io import StringIO

from copy import deepcopy

from common.adb import Adb

adb = Adb()

# 最新adb的值表, 可以进行更新
__ENV__ = {
    "EV_SYN": 0x00,  # 同步事件
    "EN_KEY": 0x01,  # keyboard
    "EV_REL": 0x02,  # 相对坐标
    "EV_ABS": 0x03,  # 绝对坐标

    "SYN_REPORT": 0,
    "SYN_CONFIG": 1,
    "SYN_MT_REPORT": 2,

    "BTN_TOUCH": 0x014a,
    "BTN_TOOL_FINGER": 0x0145,

    "REL_X": 0x00,
    "REL_Y": 0x01,
    "REL_Z": 0x02,
    "REL_RX": 0x03,
    "REL_RY": 0x04,
    "REL_RZ": 0x05,
    "REL_HWHEEL": 0x06,
    "REL_DIAL": 0x07,
    "REL_WHEEL": 0x08,
    "REL_MISC": 0x09,
    "REL_MAX": 0x0f,
    "REL_CNT": 0x10,

    "ABS_MT_TOUCH_MAJOR": 0x30,  # Major axis of touching ellipse(与ABS_MT_PRESSURE取值一样)
    "ABS_MT_TOUCH_MINOR": 0x31,  # Minor axis (omit if circular)
    "ABS_MT_WIDTH_MAJOR": 0x32,  # Major axis of approaching ellipse
    "ABS_MT_WIDTH_MINOR": 0x33,  # Minor axis (omit if circular)
    "ABS_MT_ORIENTATION": 0x34,  # Ellipse orientation
    "ABS_MT_POSITION_X": 0x35,  # Center X ellipse position(x坐标)
    "ABS_MT_POSITION_Y": 0x36,  # Center Y ellipse position(y坐标)
    "ABS_MT_TOOL_TYPE": 0x37,  # Type of touching device
    "ABS_MT_BLOB_ID": 0x38,  # Group a set of packets as a blob
    "ABS_MT_TRACKING_ID": 0x39,  # Unique ID of initiated contact(追踪的ID)
    "ABS_MT_PRESSURE": 0x3a,  # Pressure on contact area(按压力度)

    "ABS_MAX": 0x3f,
    "ABS_CNT": 0x40,

    "UP": 0,  # EN_KEY的value
    "DOWN": 1,

    "DEVICE": "/dev/input/event15"  # 需要改变
}

__EIS__ = {}


class _Env(object):
    @property
    def ENV(self) -> dict:
        if not hasattr(_Env, '__ENV__'):
            self.reload_env()
            _Env.__ENV__ = __ENV__
        return getattr(_Env, '__ENV__')

    @property
    def EIS(self) -> dict:
        if not hasattr(_Env, '__EIS__'):
            self.reload_eis()
            _Env.__EIS__ = __EIS__
        return getattr(_Env, '__EIS__')

    def reload_env(self):
        global __ENV__
        device_values = self.get_all_input_device()
        device_labels = self.get_all_input_device(is_label=True)
        for index in range(0, len(device_labels)):
            device_value = dict(device_values[index])
            device_label = dict(device_labels[index])

            # INPUT_PROP_DIRECT是监听指令的标志
            if device_label["input"] is "INPUT_PROP_DIRECT":
                __ENV__["DEVICE"] = device_label["device"]

            for key, event in device_label["events"].items():
                for i in range(0, len(event)):
                    if event[i] != device_value["events"][key][i]:
                        __ENV__[event[i]] = int(device_value["events"][key][i], 16)

        print(__ENV__["DEVICE"])

    def reload_eis(self):
        """
        一条完整的指令: 准备 -> 动作 -> 结束
        """
        device_name = adb.get_device_info()
        print(device_name)
        self.get_origin_eis("")

    @staticmethod
    def get_all_input_device(is_label=False) -> list:
        """
        device detail:
        {
            'device' : '/dev/input/event4',
            'events' : {
                'SW  (0005)': ['0002', '0004', '0006', '000e', '000f', '0010']
            },
            'input': None
        }
        """
        if is_label:
            all_devices = adb.run(' shell getevent -pl')
        else:
            all_devices = adb.run(' shell getevent -p')

        reader = StringIO(all_devices)
        colon_sep = re.compile(r"\s*:\s*")
        space_sep = re.compile(r"\s+")

        read_event, read_input, event_name, devices, device = False, False, "", [], OrderedDict()
        line = reader.readline()
        while len(line) > 0:
            line = line.replace("\n", "").strip()
            if line.count("device"):
                if device:
                    devices.append(device)
                    device = OrderedDict()

                read_event = False
                read_input = False
                device["device"] = colon_sep.split(line)[1]
                line = reader.readline()
                continue

            if line.count("events"):
                read_event = True
                line = reader.readline()
                continue

            if line.count("input"):
                read_event = False
                read_input = True
                line = reader.readline()
                continue

            if read_event:
                fileds = colon_sep.split(line)
                if line.count("value"):
                    fileds = fileds[0:-1]

                if len(fileds) == 2:
                    event_name = fileds[0]
                    if not device.get("events", None):
                        events = dict()
                    else:
                        events = device["events"]

                    events[event_name] = space_sep.split(fileds[1])
                    device["events"] = events

                if len(fileds) == 1:
                    device["events"][event_name] += space_sep.split(fileds[0])

                line = reader.readline()
                continue

            if read_input:
                if line.count("none"):
                    device["input"] = None
                else:
                    device["input"] = line

            line = reader.readline()

        if device:
            devices.append(device)

        return devices

    def get_origin_eis(self, event, time=5, count=100, message="") -> list:
        """
        获取事件指令集合(指令已经被切分)
        :param event: 过滤的事件名称
        :param time: 基于时间获取指令
        :param count: 基于数量获取指令
        :param message: 提示信息
        """
        try:
            print(message)
            eis_bytes = self._get_origin_eis(pattern=event, time=time, count=count)

            re_first = re.compile(r"^/dev/input/event.*")
            re_last_1 = re.compile(r".*EV_ABS\s+ABS_MT_TRACKING_ID\s+ffffffff$")
            re_last_2 = re.compile(r".*EV_SYN\s+SYN_REPORT\s+00000000$")

            all_eis = str(eis_bytes).split("\n")
            first, last_1, last_2, length = 0, 0, 0, len(all_eis)
            for index in range(0, length):
                f = all_eis[index].strip()
                l = all_eis[length - index - 1].strip()
                if first == 0 and re_first.match(f):
                    first = index

                # last_1 和 last_2 相距很近, 先确定last_2, 然后查找last_1, 二者一旦确定将不会再改变
                if last_1 == 0 and re_last_2.match(l):
                    last_2 = length - index

                if last_2 != 0 and last_1 == 0 and re_last_1.match(l):
                    last_1 = length - index

                all_eis[index] = f

            if last_2 != 0 and first != 0:
                return all_eis[first:last_2]
            else:
                self.get_origin_eis(event, time, count, message)
        except Exception:
            pass

    @staticmethod
    def _get_origin_eis(pattern, time=5, count=100):
        """
        获取指令, 6.0(包括6.0)以上的可以基于指令次数进行获取, 以下的版本只能基于时间进行获取
        :param pattern: 过滤的事件
        :param time: 基于时间的统计 (需要多次触发, 单次触发可能没有结果输出)
        :param count: 基于指令次数的统计
        :return:
        """
        command = """
        count=0
        wc=0
        if $(command -v wc > /dev/null 2>&1); then
            wc=1
        fi

        if [ ${wc} -eq 1 ]; then
            rm -rf /sdcard/event.txt
            getevent -l|grep PATTERN > /sdcard/event.txt &
        else
            getevent -l|grep PATTERN &
        fi

        pid=$(set `ps |grep -E '^shell.*getevent$'` && echo $2)
        while true
        do
            if [ ${wc} -eq 0 ]; then
                let count=count+1
            fi

            sleep 1

            if [ ${wc} -eq 1 ]; then
                if [ ${wc} -a $(cat /sdcard/event.txt|wc -l) -gt COUNT ]; then
                    kill -9 ${pid}
                    cat /sdcard/event.txt
                    break
                fi
            else
                if [ ${count} -ge TIME ]; then
                    kill -9 ${pid}
                    break
                fi
            fi
        done
        """
        command = command.replace("PATTERN", pattern).replace("TIME", str(time)).replace("COUNT", str(count))
        process = os.popen("{} shell '{}'".format(adb.adb_path, command))
        output = process.read()
        return output

    @staticmethod
    def split(origin_eis: list) -> list:
        """
        将原始事件指令块切分成组, 每一个组包含一个命令的指令集合
        :param origin_eis: 原始事件指令块(获取的原始的eis)
        """
        re_last_1 = re.compile(r".*EV_ABS\s+ABS_MT_TRACKING_ID\s+ffffffff$")
        re_last_2 = re.compile(r".*EV_SYN\s+SYN_REPORT\s+00000000$")

        eis_group = []
        length = len(origin_eis)
        first, last_1, last_2 = 0, 0, 0
        for index in range(0, length):
            cur = origin_eis[index]
            if last_2 == 0 and re_last_1.match(cur):
                last_1 = index

            if last_1 != 0 and last_2 == 0 and re_last_2.match(cur):
                last_2 = index
                if index + 1 <= length:
                    eis_group.append(origin_eis[first:last_2 + 1])
                    first = last_2 + 1
                    last_1, last_2 = 0, 0

        return eis_group

    @staticmethod
    def parse_group_eis(group):
        """
        start, 命令开始; middle, 命令主题; end, 命令结尾
        :param group: 一个原始的指令集合(切分后的组)
        """
        start, end, middle = [], [], []
        is_start, is_end, is_middle = True, False, False
        for es in group:
            es = re.subn("^/dev.*:\s+", "", es, 1)[0]
            if es.count("ABS_MT_POSITION_X"):
                is_start = False
                is_middle = True

            if es.count("ABS_MT_TRACKING_ID") and es.count("ffffffff"):
                is_end = True
                is_middle = False

            if is_start:
                start.append(es)

            if is_middle:
                middle.append(es)

            if is_end:
                end.append(es)

        return start, middle, end

    @staticmethod
    def generate_command_template(all_group: list) -> tuple:
        """
        :param all_group: 所有已经解析过group
        """
        start, middle, end = [], [], []
        for group in all_group:
            s = group[0]
            m = group[1]
            e = group[2]

            if not start and not middle and not end:
                start, middle, end = deepcopy(s), deepcopy(m), deepcopy(e)

            # 处理:1.传递自定义函数 2.统一集中处理
            for i in s:
                pass

            for i in m:
                pass

            for i in e:
                pass

        return start, middle, end

    @staticmethod
    def validate():
        pass


Env = _Env()

if __name__ == '__main__':
    strs = """
        /dev/input/event15: 0001 014a 00000001
        /dev/input/event15: 0001 0145 00000001
        /dev/input/event15: 0003 0039 00000000
        /dev/input/event15: 0003 0035 0000020d
        /dev/input/event15: 0003 0036 000002aa
        /dev/input/event15: 0003 0030 00000007
        /dev/input/event15: 0003 003a 00000007
        /dev/input/event15: 0000 0000 00000000
        /dev/input/event15: 0003 0039 ffffffff
        /dev/input/event15: 0000 0000 00000000
        /dev/input/event15: 0001 014a 00000000
        /dev/input/event15: 0001 0145 00000000
        /dev/input/event15: 0000 0000 00000000
    """

    strs = strs.split("\n")
    res = ""
    for s in strs:
        if len(s.replace(":", "").lstrip()) == 0:
            continue
        ln = s.replace(":", "").lstrip().split(" ")
        ln[1] = str(int('0x' + ln[1], 16))
        ln[2] = str(int('0x' + ln[2], 16))
        ln[3] = str(int('0x' + ln[3], 16))

        res = res + "adb shell sendevent " + " ".join(ln) + " && \\\n"

    s = Env.get_origin_eis('event2', time=10, count=100, message="请点击:")

    g = Env.split(s)
    for i in range(0, len(g)):
        s, m, e = Env.parse_group_eis(g[i])
        for j in s:
            print(j)

        print()

        for j in m:
            print(j)

        print()

        for j in e:
            print(j)

        print("\n=======================\n")
