import hashlib
import hmac
import json
import random
import time

def linkiot(DeviceName,ProductKey,DeviceSecret,server='iot-as-mqtt.cn-shanghai.aliyuncs.com'):
    serverUrl = server
    ClientIdSuffix = "|securemode=3,signmethod=hmacsha256,timestamp="
    # 拼合 -> 明文密码
    Times = str(int(time.time()))  # 获取登录时间戳
    Server = ProductKey+'.'+serverUrl    # 服务器地址
    ClientId = DeviceName + ClientIdSuffix + Times +'|'  # ClientId
    userName = DeviceName + "&" + ProductKey
    PasswdClear = "clientId" + DeviceName + "deviceName" + DeviceName +"productKey"+ProductKey + "timestamp" + Times
    # 加密
    h = hmac.new(bytes(DeviceSecret,encoding='UTF-8'),digestmod=hashlib.sha256)  # 使用密钥
    h.update(bytes(PasswdClear,encoding='UTF-8'))
    Passwd = h.hexdigest()
    return Server,ClientId,userName,Passwd

# 阿里Alink协议实现（字典传入，json str返回）
def Alink(params):
    AlinkJson = {"id": random.randint(0, 999999),
                 "version": "1.0",
                 "params": params,
                 "method": "thing.event.property.post"}
    return json.dumps(AlinkJson)
