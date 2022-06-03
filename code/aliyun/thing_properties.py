# 设备各个阿里云物模型参数
from subprocess import check_output

class DeviceProperties:
    def __init__(self):
        self.RunningState = None
        self.EventId = ""
        self.InflowOutflowStatus = 0
        self.OssConnectionState = 0

    @property
    def IpAddress(self):
        cmd = "hostname -I"
        return check_output(cmd, shell=True).decode("utf-8").strip()


device_properties = DeviceProperties()
