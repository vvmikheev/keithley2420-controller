import pyvisa

"""
If everything is connected in the right way, this script will print all avaliable devices
"""

rm = pyvisa.ResourceManager()
devices = rm.list_resources()

print(devices)