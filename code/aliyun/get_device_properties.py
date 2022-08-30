from aliyunsdkcore import client
from aliyunsdkiot.request.v20180120 import RegisterDeviceRequest
from aliyun.aliyun_constants import OSS_id, OSS_key, iotInstanceId, ProductKey, DeviceName
import json

clt = client.AcsClient(OSS_id, OSS_key, 'cn-shanghai')

def get_device_properties():
    request = RegisterDeviceRequest.RegisterDeviceRequest()
    request.set_accept_format('json')  # 设置返回数据格式，默认为XML，此例中设置为JSON
    request.set_IotInstanceId(iotInstanceId)
    request.set_ProductKey(ProductKey)
    request.set_DeviceName(DeviceName)
    request.set_action_name("QueryDevicePropertyStatus")
    result = clt.do_action_with_exception(request)
    json_props = json.loads(result.decode())

    mapping = {elem['Identifier'] : elem['Value'] for elem in json_props['Data']['List']['PropertyStatusInfo']}
    return mapping
