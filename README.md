# CPU and GPU temperature display for Deepcool Digital ch650 USB-device on Linux
Python script for DeepCool CH650 DIGITAL case displaying CPU and GPU temperatures and usages.

# First start
Im not sure but before start the script you may need to have installed and use sensors.
Run sensors-detect and get your sensor name for your CPU.
Then replace the sensor name nct6798 in line 141 with your

cputemp = round(psutil.sensors_temperatures()['nct6798'][0].current)

You need root to get it work.
