# python-deepcool ch650 DIGITAL
Python script for DeepCool CH650 DIGITAL case

# First start
Im not sure but before start the script you may need to have installed and use sensors
Run sensors-detect and get the driver name for you CPU sensor.
Then sensor nct6798 in line 141 with your

cputemp = round(psutil.sensors_temperatures()['nct6798'][0].current)

