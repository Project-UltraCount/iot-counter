import oss2
import time

from aliyun.thing_properties import device_properties
from aliyun.aliyun_constants import OSS_id, OSS_key, OSS_endpoint, OSS_bucket_name, DeviceName, FILE_UPDATE_FREQUENCY
from device.device_constants import LCD_LINE_1
from device.lcd import lcd_display


class OSS:
    def __init__(self, event_id, inflow_outflow_status, device_name=DeviceName, id=OSS_id, key=OSS_key,
                 endpoint=OSS_endpoint, bucket_name=OSS_bucket_name):
        self.event_id = event_id
        self.updating = True
        self.inflow_outflow_status = inflow_outflow_status
        self.OSS_object_name_1 = self.OSS_object_name_2 = ""
        self.write_inflow = self.write_outflow = None
        self.__connect_oss(id, key, endpoint, bucket_name)
        self.__initialise_oss(device_name)
        self.start_counting()

    def __connect_oss(self, id, key, endpoint, bucket_name):
        # Aliyun account and accessKey
        self.auth = oss2.Auth(id, key)
        print('using %s : %s' % (id, key))
        # endpoint to the region where the bucket is located
        self.bucket = oss2.Bucket(self.auth, endpoint, bucket_name, connect_timeout=1000)
        print("Success: %s:%s" % (endpoint, bucket_name))

    def __initialise_oss(self, device_name): # create directories on the server
        self.bucket.put_object(f"{self.event_id}/", b'')
        self.bucket.put_object(f"{self.event_id}/{device_name}/", b'')
        device_properties.OssConnectionState = 1
        lcd_display("OSS connected", LCD_LINE_1)

    def start_counting(self, device_name=DeviceName):
        data = str(int(time.time() * 1000)) + " " + str(0) + "\n"
        if self.inflow_outflow_status == 1:
            self.OSS_object_name_1 = f"{self.event_id}/{device_name}/" + "write_inflow.txt"
            self.write_inflow = self.bucket.append_object(self.OSS_object_name_1, 0, data) # event starting time

        elif self.inflow_outflow_status == 2:
            self.OSS_object_name_2 = f"{self.event_id}/{device_name}/" + "write_outflow.txt"
            self.write_outflow = self.bucket.append_object(self.OSS_object_name_2, 0, data)

        elif self.inflow_outflow_status == 3:
            self.OSS_object_name_1 = f"{self.event_id}/{device_name}/" + "write_inflow.txt"
            self.OSS_object_name_2= f"{self.event_id}/{device_name}/" + "write_outflow.txt"
            self.write_inflow = self.bucket.append_object(self.OSS_object_name_1, 0, data)
            self.write_outflow = self.bucket.append_object(self.OSS_object_name_2, 0, data)

    def append_file(self, inflow, outflow):
        time_data = str(int(time.time() * 1000))
        data1 = time_data + " " + str(inflow) + "\n"
        data2 = time_data + " " + str(outflow) + "\n"
        if self.inflow_outflow_status == 1:
            self.write_inflow = self.bucket.append_object(self.OSS_object_name_1, self.write_inflow.next_position, data1)
            print("inflow count appended")
        elif self.inflow_outflow_status == 2:
            self.write_outflow = self.bucket.append_object(self.OSS_object_name_2, self.write_outflow.next_position, data2)
            print("outflow count appended")
        elif self.inflow_outflow_status == 3:
            self.write_inflow = self.bucket.append_object(self.OSS_object_name_1, self.write_inflow.next_position, data1)
            self.write_outflow = self.bucket.append_object(self.OSS_object_name_2, self.write_outflow.next_position, data2)
            print("both counts appended")

    def thread_update_oss_file(self, counting):
        # update oss file every UPDATE_FREQUENCY time
        while self.updating:
            time.sleep(FILE_UPDATE_FREQUENCY)
            num1, num2 = counting.get_flow_count()
            self.append_file(num1, num2)
            print("data string appended")

    def thread_stop_update(self):
        self.updating = False

    def thread_resume_update(self):
        self.updating = True
