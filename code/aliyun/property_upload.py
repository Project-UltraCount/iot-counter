from threading import Thread

from aliyun import aliLink
import time
# 链接信息
from aliyun.aliyun_constants import POST
from aliyun.thing_properties import device_properties

uploading = True
mqtt = None

thread = None
def start_upload(_mqtt):
    global mqtt
    global thread
    mqtt = _mqtt
    def thread_upload():
        while True:
            if uploading:
                upload()
            time.sleep(1)
    if thread is None:
        thread = Thread(target=thread_upload)
        thread.start()

def upload():
    # 构建与云端模型一致的消息结构
    updateMsn = {
        'RunningState': device_properties.RunningState,
        'IPAddress': device_properties.IpAddress,
        'EventId': device_properties.EventId,
        'InflowOutflowStatus': device_properties.InflowOutflowStatus,
        'OssConnectionState': device_properties.OssConnectionState
    }
    JsonUpdateMsn = aliLink.Alink(updateMsn)
    # 定时向阿里云IOT推送我们构建好的Alink协议数据
    mqtt.push(POST, JsonUpdateMsn)
    print(JsonUpdateMsn)

def stop_mqtt():
    global uploading
    uploading = False

def resume_mqtt():
    global uploading
    uploading = True
