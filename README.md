# CPU and GPU temperature display for Deepcool Digital ch650 USB-device on Linux
Python script for DeepCool CH650 DIGITAL case displaying CPU and GPU temperatures and usages.

# First start
You need to have installed lm-sensors. Then start sensors-detect as root and follow the steps.
Load your CPU sensors kernel modules and them verify with command: sensors

After that replace the sensor name nct6798 on line 114 with your

cputemp = round(psutil.sensors_temperatures()['nct6798'][0].current)

You need root to get it work.

