import serial
import os
import time
from datetime import datetime
import psutil
import math
import GPUtil
import clr

clr.AddReference('OpenHardwareMonitorLib')
from OpenHardwareMonitor.Hardware import Computer
#==============================
#SETTINGS/SETUP
#==============================

logging = True
# Logging toggle, so far only logs crashes and exits
safety = True
# Experimental toggle, mainly to do with emergency shutoff in case of thermal runaway
cpu_threshold = 90
gpu_threshold = 70
# Safety toggle settings

c = Computer()
hardware_index = 1
# On my personal system this is my CPU with the current enables
obj_Disk = psutil.disk_usage('c:\\')
# Drive letter you will be reading
c.CPUEnabled = True
c.GPUEnabled = True
c.MainboardEnabled = True
c.FanControllerEnabled = True
# Leave all four enabled to be able to read CPU and GPU temperatures
c.Open()
c.Hardware[hardware_index].Update()
updateTime = 2
# Set refresh rate

cpu_temp = ''
cpu_index = ''
rpm = ''
gpu_temp = ''
# Declare variables for later use
#==============================
#LOGGING
#==============================

def save_log():
    log.flush()
    os.fsync(log.fileno())

if logging:
    log_name = str(datetime.now().strftime("%Y-%m-%d_%H_%M_%S"))+".txt"
    log = open(log_name, 'w')
    print("[" + str(datetime.now()) + "]: Starting.")
    save_log()



def sendData(temp, rpm, gpu, free_disk, free_mem, procs):
    try:
        connection = serial.Serial('COM14') # Change this to match your COM port!
        data = str(temp) + ',' + str(rpm) + ',' + str(free_mem) + ',' + str(free_disk) + ',' + str(gpu) + ',' + str(procs) + '/'
        connection.write(data.encode())
        print("Data written", data.encode())
        connection.close  
    except Exception as e:
        print(e)
# Sends data to compatible ESP32/Display Combo

for i in range(len(c.Hardware[hardware_index].Sensors)):
    # print(c.Hardware[hardware_index].Sensors[i].Identifier)
    if "/temperature" in str(c.Hardware[hardware_index].Sensors[i].Identifier):
        cpu_index = i
        break;
    c.Hardware[hardware_index].Update()
# Find index of CPU package, in Open Hardware Manager this is always the first CPU temperature entry, and record it for later
# Scanning all devices every (refresh rate) would be wildly inefficient and leads to CPU heating

while 1:
    #CPU
    cpu_usage = (int(math.ceil(psutil.cpu_percent())))
    cpu_temp = (int(c.Hardware[hardware_index].Sensors[cpu_index].get_Value()))
    #GPU TEMP
    gpu = GPUtil.getGPUs()[0]
    gpu_temp = int(gpu.temperature)
    #MEMORY
    free_mem = (int((psutil.virtual_memory().total - psutil.virtual_memory().used) / (1024 * 1024)))
    used_mem = (int(psutil.virtual_memory().used) / (1024 * 1024))
    #DISK
    free_disk = (int(obj_Disk.free / (1024.0 ** 3)))

    c.Hardware[hardware_index].Update()
    # Make sure to call update after scanning

    if safety:
        if (cpu_temp >= cpu_threshold) or (gpu_temp >= gpu_threshold):
            if cpu_temp >= cpu_threshold:
                print("["+str(datetime.now())+"]: CPU Overheating.")
                print("[" + str(datetime.now()) + "]: Shutting Down.")
                save_log()
            if gpu_temp >= gpu_threshold:
                print("[" + str(datetime.now()) + "]: GPU Overheating.")
                print("[" + str(datetime.now()) + "]: Shutting Down.")
                save_log()
            exit()
            # realistically neither should ever trigger, especially gpu threshold
            # however repeatedly scanning with Open Hardware Manager has been shown to generate excess heat

    proc_counter = 0
    for proc in psutil.process_iter():
        proc_counter += 1

    sendData(cpu_usage, cpu_temp, gpu_temp, free_disk, used_mem, proc_counter)
    # Send data out to receiver
    time.sleep(updateTime)
    # Wait for update time before restart
    
