import time
import requests
import smbus2
import sys

token = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

#accelerator address
acc_address = 0x1d

#register address
status = 0x00
x_msb = 0x01
x_lsb = 0x02
y_msb = 0x03
y_lsb = 0x04
z_msb = 0x05
z_lsb = 0x06
xyz_data_cfg = 0x0e
ctrl_reg1 = 0x2a
crtl_reg2 = 0x2b
crtl_reg3 = 0x2c
ctrl_reg4 = 0x2d
ctrl_reg5 = 0x2e

#data registers
xyz_data_cfg_fs_2g = 0
xyz_data_cfg_fs_4g = 1
xyz_data_cfg_fs_8g = 2
ctrl_reg1_standby = 0
ctrl_reg1_active = 1

#Line notify API
def linenotify():
    payload = {'message': 'something is moving...'}
    headers = {'Authorization' : 'Bearer ' + token}
    requests.post('https://notify-api.line.me/api/notify', data = payload, headers = headers)

def main():
    bus = smbus2.SMBus(1)
    bus.write_byte_data(acc_address, xyz_data_cfg, xyz_data_cfg_fs_2g)
    bus.write_byte_data(acc_address, ctrl_reg1, ctrl_reg1_active)
    
    while True:
        data = bus.read_i2c_block_data(acc_address, x_msb, 0x06)
        
        #data conversion
        data_x = (data[0]*256 + data[1]) // 16
        if data_x > 2047:
            data_x -= 4096
            
        data_y = (data[2]*256 + data[3]) // 16
        if data_y > 2047:
            data_y -= 4096
            
        data_z = (data[4]*256 + data[5]) // 16
        if data_z > 2047:
            data_z -= 4096
            
        acc_x = data_x / 1024.0
        acc_y = data_y / 1024.0
        acc_z = data_z / 1024.0
        
        #notification threshold
        if abs(acc_x) > 0.2 or abs(acc_y) > 0.2 or abs(acc_z) > 1.2 or abs(acc_z) < 0.7:
            linenotify()
            time.sleep(5.0)

        print(f"x: {str(acc_x)} - {str(data_x)}")
        print(f"y: {str(acc_y)} - {str(data_y)}")
        print(f"z: {str(acc_z)} - {str(data_z)}")
        
        time.sleep(1.0)
    return
    
if __name__ == "__main__":
    main()
