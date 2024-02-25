from os import path
import time
import hid
import psutil
import glob

VENDOR_ID = 0x3633  # DeepCool's Vendor ID
PRODUCT_ID = 0x0005  # CH650's Product ID
INTERVAL = 2

'''
find_gpu_cards will search for hwmon and return dict
with keys {'card'} and values the system path to hardware monitoring directories
acording to kernel source files, all GPU drivers should provide this information
into /sys/class/drm/card?/device/hwmon/hwmon?/
'''

def find_gpu_cards() -> dict:
    cards = {}
    card_pattern = '/sys/class/drm/card*/device/hwmon/hwmon*/name'
    hwmon_names = glob.glob(card_pattern)
    for hwmon_name_file in hwmon_names:
        with open(hwmon_name_file, "r", encoding = "utf-8") as _f:
            _card = hwmon_name_file.split('/')[4]
            _hwmon_dir = path.dirname(hwmon_name_file)
            cards[_card] = _hwmon_dir
    return dict(sorted(cards.items()))

'''
Old function bellow, if gputemp it's not working
the gpu temperature could be read from temp1_input

def get_GPUtemp(cards: dict) -> int:
    ret_data = 0
    if cards:
        fgpu = cards.get('card0')

        with open(fgpu + '/temp1_input', "r", encoding="utf-8") as _gputemp:
            ret_data = int(_gputemp.read().strip()) // 1000

    return ret_data
'''

def get_gpu_load(cards: dict) -> int:
    gpu_percent = 0
    if cards:
        fgpu = cards.get('card0')

        with open(fgpu + '/../../gpu_busy_percent', "r", encoding="utf-8") as _gpu_usage:
            gpu_percent = int(_gpu_usage.read().strip())

    return gpu_percent


def get_greenbar_value(input_value):
    return (input_value - 1) // 10 + 1

'''

 2 - CPU Usage green bar, one number from 0 to 10
 3 - CPU first value - one number
 4 - CPU second value - one number
 5 - CPU last value - one number
 6 - GPU LOAD display load usage - 19 degree in Celsius, 35 - Fahrenheit, 76 - GPU USAGE in %,
 7 - GPU usage green bar
 8 - the same as CPU number 3 but for GPU - one number
 9 - GPU second value - one number
 10 - GPU last value - one number

'''

def prepare_data(cpuvalue = 0, cpuload = 0, gputemp = 0, gpuload = 0, mode = 'usage'):

    gpu_data = [int(char) for char in str(gputemp)]

    basic_data = [16, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    cpu_data = [int(char) for char in str(cpuvalue)]
    basic_data[2] = get_greenbar_value(cpuload)
    basic_data[7] = get_greenbar_value(gpuload)
    if  mode == 'usage':
        basic_data[1] = 76
        basic_data[6] = 76
        gpu_load = [int(char) for char in str(gpuload)]
        gpu_data = gpu_load
    elif mode == 'start':
        basic_data[1] = 170
        basic_data[6] = 170
        return basic_data
    elif mode == 'temp':
        basic_data[1] = 19
        basic_data[6] = 19
    if len(cpu_data) == 1:
        basic_data[5] = cpu_data[0]
    elif len(cpu_data) == 2:
        basic_data[4] = cpu_data[0]
        basic_data[5] = cpu_data[1]
    elif len(cpu_data) == 3:
        basic_data[3] = cpu_data[0]
        basic_data[4] = cpu_data[1]
        basic_data[5] = cpu_data[2]
    if len(gpu_data) == 1:
        basic_data[10] = gpu_data[0]
    elif len(gpu_data) == 2:
        basic_data[9] = gpu_data[0]
        basic_data[10] = gpu_data[1]
    elif len(gpu_data) == 3:
        basic_data[8] = gpu_data[0]
        basic_data[9] = gpu_data[1]
        basic_data[10] = gpu_data[2]

    return basic_data

def get_temperature():
    cputemp = round(psutil.sensors_temperatures()['nct6798'][0].current)
    gputemp = round(psutil.sensors_temperatures()['amdgpu'][0].current)
    # comment line above and uncomment second line if you does not have amdgpu
    # but you are still using amd gpu
    # gputemp = get_GPUtemp(cards)
# We always need cpuload and gpuload, this is for the green bars
    gpuload = get_gpu_load(cards)
    cpuload = round(psutil.cpu_percent())
    return prepare_data(cpuvalue = cputemp, cpuload = cpuload, gputemp = gputemp, gpuload = gpuload, mode = 'temp')

def get_usage():
# We always need cpuload and gpuload, this is for the green bars
    usage = round(psutil.cpu_percent())
    gpuload = get_gpu_load(cards)
    return prepare_data(cpuvalue = usage, cpuload = usage, gpuload = gpuload, mode = 'usage')

try:
    cards = find_gpu_cards()
    h = hid.device()
    h.open(VENDOR_ID, PRODUCT_ID)
    h.set_nonblocking(1)
    h.write(prepare_data(mode = "start"))
    while True:
        h.set_nonblocking(1)
        h.write(get_temperature())
        time.sleep(INTERVAL)
        h.write(get_usage())
        time.sleep(INTERVAL)
except IOError as ex:
    print(ex)
    print("Ensure that the DeepCool CH650 DIGITAL is connected and the script has the correct Vendor ID and Product ID.")
    print("run lsusb to obtain Vendor ID and Product ID")
    print("take this line Bus 001 Device 003: ID 3633:0005 DeepCool CH560 DIGITAL")
    print("Your Vendor ID is 3633 and Product ID is 0005")
except KeyboardInterrupt:
    print("Script terminated by user.")
finally:
    h.close()


# /sys/class/drm/card*/device/hwmon/*
