# 三元素（iot后台获取）
ProductKey = 'ha9aL7yJNmT'
DeviceName = 'device1'
DeviceSecret = "babcc07ff58e24027b954b30545375b3"

# topic (iot后台获取)
POST = '/sys/ha9aL7yJNmT/device1/thing/event/property/post'  # 上报消息到云
POST_REPLY = '/sys/ha9aL7yJNmT/device1/thing/event/property/post_reply'  # 云端响应属性上报
SET = '/sys/ha9aL7yJNmT/device1/thing/service/property/set'  # 订阅云端指令

# OSS constants to be declared
OSS_id = "LTAI5t5jK7G15gb9D7yRMV16"
OSS_key = "Uy4lVE2ZWqVdZLxWKP7Vl2u7iGvzco"
OSS_endpoint = r"https://oss-ap-southeast-1.aliyuncs.com"
OSS_bucket_name = "projectultracount"
OSS_timeout = 1000
FILE_UPDATE_FREQUENCY = 10  # only need to upload, writing to local file is not needed
