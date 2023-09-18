import asyncio
from aioconsole import ainput
from bleak import BleakClient, discover

import os
from datetime import datetime

# Define path and name of output file
#root_path = os.environ["HOME"]
#output_file = r"C:\Users\Celia\Desktop\ble data.csv"
current_time = datetime.now()
time_stamp = current_time.timestamp()
date_time = datetime.fromtimestamp(time_stamp)
str_date_time = date_time.strftime("%Y%m%d")
#path1 = r"C:\\Users\\Celia\\Desktop\\"
path1 = r"C:\\Users\\Celia\\OneDrive - Johns Hopkins\\00. Chinchilla Current Source\\Data_Reconnect\\"
#path1 = r"/Users/celia/Library/CloudStorage/OneDrive-JohnsHopkins/00. Chinchilla Current Source/Data_Reconnect/"
path2 = str_date_time
output_file = path1 + path2 + "Data.csv"


async def data_client(device):
    def handle_rx(_: int, data: bytearray):
        print("received:", data)
        column_names = ["Date","Time","Ch0", "Ch1", "Ch2", "Ch3"]
        f=open(output_file, "a+")
        if os.stat(output_file).st_size == 0:
            print("Created file.")
            f.write(",".join([str(name) for name in column_names]) + ",\n")
        else:
            #print(data,"\n")
            datastr = bytearray.decode(data)
            current_time = datetime.now()
            time_stamp = current_time.timestamp()
            date_time = datetime.fromtimestamp(time_stamp)
            str_date_time = date_time.strftime("%d-%m-%Y, %H:%M:%S")
            f.write(f"{str_date_time},{datastr[0:4].strip()},{datastr[5:9]},{datastr[10:14].strip()},{datastr[15:19].strip()},\n")
    
    while True:
        try:
            async with BleakClient(device, timeout=30) as client:
                await client.start_notify(read_characteristic, handle_rx)
                print("Connected to device:", device)

                while client.is_connected:
                    bytes_to_send = b''  # No need for user input, adjust as needed

                    try:
                        await client.write_gatt_char(write_characteristic, bytes_to_send)
                    except Exception as e:
                        print("Error writing GATT characteristic:", e)

                    await asyncio.sleep(1)  # Adjust the delay if needed
        except asyncio.CancelledError:
            print("Cancelled monitoring")
        except Exception as e:
            print("Disconnected due to:", e)
            print("Attempting to reconnect...")
            await asyncio.sleep(5)  # Wait before trying to reconnect

async def select_device():
    print("Scanning for Bluetooh LE hardware...")
    await asyncio.sleep(2.0)  # Wait for BLE to initialize.
    devices = await discover()

    print("Please select device: ")
    for i, device in enumerate(devices):
        print(f"{i}: {device.name}")
    print("99: Exit program")
    print("-1: Re-scan for BLE devices")
    response = await ainput("Select device: ")
    try:
        response = int(response.strip())
    except ValueError:
        print("Please make valid selection.")
        response = -1
    print('response', type(response), response)
    if -1 < response < len(devices):
        return devices[response].address
    elif response == 99:
        return 99
    print("Please make valid selection.")



async def main():
    #device = "A3E0539E-3CF8-867E-2B7B-1EE451EC384B" ## UUID for nRF52DK on-board chip
    #device = None
    #device = "9072C211-81C0-EA8E-71FE-031EDFE410E3" # UUID for new nRF52DK on-board chip
    device = "DD:4B:A2:62:E5:01" # BC832 module
    # ... Other device configurations ...

    keep_alive = True
    while keep_alive:
        print('Device:', device)
        if device is None:
            device = await select_device()
            if device == 99:
                keep_alive = False
        elif device:
            #print('\nCheckpoint 1 COMPLETE')
            await data_client(device)
            device = None
            print('Device disconnected. Attempting to reconnect...')
            await asyncio.sleep(5)  # Wait before trying to reconnect

# For nRF52DK on-board chip:
write_characteristic = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E" #ARDUINO
read_characteristic = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E" #ARDUINO

if __name__ == "__main__":
    asyncio.run(main())
