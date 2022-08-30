# 设备各个阿里云物模型参数
import time
from subprocess import check_output
import json
from threading import Thread
from os.path import exists

class DeviceProperties:
    def __init__(self):
        if exists(r'properties_cache.json'):
            with open(r'properties_cache.json', 'r') as f:
                self.__dict__ = json.load(f)
        else:
            self.RunningState = None
            self.EventId = ""
            self.InflowOutflowStatus = 0
            self.OssConnectionState = 0

        def cache():
            while True:
                with open(r'properties_cache.json', 'w') as f:
                    json.dump(self.__dict__, f)
                time.sleep(5)
                
        def tmp():
            while 1:
                print(self.__dict__)
                time.sleep(1)
                
        Thread(target=cache).start()
        Thread(target=tmp).start()
        
    @property
    def IpAddress(self):
        cmd = "hostname -I"
        return check_output(cmd, shell=True).decode("utf-8").strip()


device_properties = DeviceProperties()
