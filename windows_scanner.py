import clr
clr.AddReference('OpenHardwareMonitorLib')

from OpenHardwareMonitor.Hardware import Computer

c = Computer()
c.CPUEnabled = True
c.GPUEnabled = True
c.MainboardEnabled = True
c.FanControllerEnabled = True
c.Open()

hardware_index = 1
# Index depends on system, or just scan them all
# currently my personal settings are 0 (empty?), 1 (cpu), 2 (gpu)

print(len(c.Hardware))
# print number of hardware devices read
print(len(c.Hardware[hardware_index].Sensors))
# print number of sensors on selected device

# print(dir(c))

c.Hardware[hardware_index].Update()

while True:
    for a in range(0, len(c.Hardware[0].Sensors)):
        print(str(c.Hardware[0].Sensors[a].Identifier))
        c.Hardware[0].Update()
    # prints all sensor's names in current hardware device

for i in range(len(c.Hardware[hardware_index].Sensors)):
    # print(c.Hardware[hardware_index].Sensors[i].Identifier)
    if "/temperature" in str(c.Hardware[hardware_index].Sensors[i].Identifier):
        print(c.Hardware[hardware_index].Sensors[i].get_Value())
        break;
    c.Hardware[hardware_index].Update()
    # example block to find and print temperature sensors in current hardware device
