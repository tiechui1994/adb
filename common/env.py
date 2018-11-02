"""
指令表
"""

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

    "DEVICE": "/dev/input/event2"  # 需要改变
}


class _Env(object):
    @property
    def ENV(self) -> dict:
        if not hasattr(_Env, '__ENV__'):
            self.reload()
            _Env.__ENV__ = __ENV__
        return getattr(_Env, '__ENV__')

    @staticmethod
    def reload():
        global __ENV__


Env = _Env()

if __name__ == '__main__':
    strs = """
        /dev/input/event15: 0001 014a 00000001
        /dev/input/event15: 0001 0145 00000001
        /dev/input/event15: 0003 0039 00000000

        /dev/input/event15: 0003 0035 00000279
        /dev/input/event15: 0003 0036 000002b1
        /dev/input/event15: 0003 0030 00000008
        /dev/input/event15: 0003 003a 00000008
        /dev/input/event15: 0000 0000 00000000

        /dev/input/event15: 0003 0035 00000267
        /dev/input/event15: 0003 0036 000002b0
        /dev/input/event15: 0003 0030 00000007
        /dev/input/event15: 0003 003a 00000007
        /dev/input/event15: 0000 0000 00000000

        /dev/input/event15: 0003 0035 0000021a
        /dev/input/event15: 0003 0036 000002da
        /dev/input/event15: 0003 0030 00000009
        /dev/input/event15: 0003 003a 00000009
        /dev/input/event15: 0000 0000 00000000

        /dev/input/event15: 0003 0035 000001d0
        /dev/input/event15: 0003 0036 00000320
        /dev/input/event15: 0003 0030 00000009
        /dev/input/event15: 0003 003a 00000009
        /dev/input/event15: 0000 0000 00000000

        /dev/input/event15: 0003 0035 00000156
        /dev/input/event15: 0003 0036 000003ae
        /dev/input/event15: 0003 0030 00000008
        /dev/input/event15: 0003 003a 00000008
        /dev/input/event15: 0000 0000 00000000

        /dev/input/event15: 0003 0036 000003ba
        /dev/input/event15: 0003 0030 0000000b
        /dev/input/event15: 0003 003a 0000000b
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
        if len(s.replace(":", "").lstrip(" ")) == 0:
            continue
        line = s.replace(":", "").lstrip(" ").split(" ")
        line[1] = str(int('0x' + line[1], 16))
        line[2] = str(int('0x' + line[2], 16))
        line[3] = str(int('0x' + line[3], 16))

        res = res + "adb shell sendevent " + " ".join(line) + " && \\\n"

    print(res.rstrip('&'))
