# -*- coding: utf-8 -*-
# import os
import random
import time

import oss2
# 以下代码展示了基本的文件上传、下载、罗列、删除用法。
# 首先初始化AccessKeyId、AccessKeySecret、Endpoint等信息。
# 通过环境变量获取，或者把诸如“<你的AccessKeyId>”替换成真实的AccessKeyId等。
# 分别以HTTP、HTTPS协议访问。
AccessId = "LTAI5t5jK7G15gb9D7yRMV16"
AccessKey = "Uy4lVE2ZWqVdZLxWKP7Vl2u7iGvzco"
endpoint = r"https://oss-ap-southeast-1.aliyuncs.com"
bucket_name = "projectultracount"
object_name = "testosterone.txt"
file_path = r"C:/Users/30847/Desktop/UltraCount_2021/Coding/example_file.txt"
data = ''

# 阿里云账号AccessKey拥有所有API的访问权限，风险很高。强烈建议您创建并使用RAM用户进行API访问或日常运维，请登录RAM控制台创建RAM用户。
auth = oss2.Auth(AccessId, AccessKey)
# yourEndpoint填写Bucket所在地域对应的Endpoint。以华东1（杭州）为例，Endpoint填写为https://oss-cn-hangzhou.aliyuncs.com。
# 填写Bucket名称。
# bucket = oss2.Bucket(auth, endpoint, bucket_name, connect_timeout=10) workable yay!
bucket = oss2.Bucket(auth, endpoint, bucket_name)


class Main:
    def __init__(self):
        if bucket.object_exists(object_name):
            start_pos = bucket.get_object(object_name).content_length
        else:
            start_pos = 0
        self.result = bucket.append_object(object_name, start_pos, "")

    def upload(self):
        n = 0
        while True:
            data = f'dummy {n}\n'
            self.result = bucket.append_object(object_name, self.result.next_position, data)
            print("appended")
            time.sleep(random.uniform(1,4))
            n += 1


def delete():
    bucket.delete_object(object_name)


delete()
demo = Main()
demo.upload()
# try:
#     # 删除存储空间。
#     bucket.delete_bucket()
# except oss2.exceptions.BucketNotEmpty:
#     print('bucket is not empty.')
# except oss2.exceptions.NoSuchBucket:
#     print('bucket does not exist')

# 创建Bucket对象，所有Object相关的接口都可以通过Bucket对象来进行
# bucket.put_object_from_file(object_name, file_path)  -----> workable yay!
# for b in islice(oss2.ObjectIterator(bucket), 10):
#     print(b.key)
