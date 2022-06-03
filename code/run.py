#!/usr/bin/python3

import json
from aliyun import aliLink, mqttd

# 消息回调（云端下发消息的回调函数）
from aliyun.aliyun_constants import SET, DeviceName, ProductKey, DeviceSecret
from aliyun.oss import OSS
from aliyun.property_upload import start_upload, stop_mqtt
from aliyun.thing_properties import device_properties
from device import components
from device.components import clean_up
from device.counting import Counting


def on_message(client, userdata, msg):
    # print(msg.payload)
    params = json.loads(msg.payload)['params']
    device_properties.RunningState = params['RunningState']
    device_properties.EventId = params['EventId']
    device_properties.InflowOutflowStatus = params['InflowOutflowStatus']
    print(params)


# 连接回调（与阿里云建立链接后的回调函数）
def on_connect(client, userdata, flags, rc):
    pass


# device setup
components.setup()
components.wifi_check_status()
# 实现设备和iot平台的连接
Server, ClientId, userName, Password = aliLink.linkiot(DeviceName, ProductKey, DeviceSecret)
# mqtt连接
mqtt = mqttd.MQTT(Server, ClientId, userName, Password)
mqtt.subscribe(SET)  # 订阅服务器下发消息topic
mqtt.begin(on_message, on_connect)
start_upload(mqtt) # mqtt上传iot连接信息

counter = None
oss = None

while not device_properties.RunningState:
    pass

try:
    while device_properties.RunningState:
        oss = OSS(device_properties.EventId, device_properties.InflowOutflowStatus)
        counter = Counting(device_properties.InflowOutflowStatus)
        counter.thread_start_counting()
        oss.thread_update_oss_file(oss)

    # Close the Connection
    counter.thread_stop_counting()
    oss.thread_stop_update()
    stop_mqtt()
    clean_up()

except KeyboardInterrupt:
    # Close the Connection
    counter.thread_stop_counting()
    oss.thread_stop_update()
    stop_mqtt()
    clean_up()
