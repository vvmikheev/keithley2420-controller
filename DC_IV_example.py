from SMU_device import SMUDevice
import numpy as np
import matplotlib.pyplot as plt

instrument_id = 'GPIB0::24::INSTR'

# creating SMU object
smu = SMUDevice(instrument_id)
smu.connect()  # call of this function is obligatory

# setting up sense subsystem and list sweep
smu.setup_sense_subsystem(autorange=False, rang=1e-9, compl=1e-9, nplc=0.1)
smu.staircase_sweep(-1, 1, 20, delay=1)

# enabling output and do the measure
smu.enable_output()
smu.measure()
smu.wait()
smu.disable_output()

# checking errors and getting results
smu.check_for_errors()
data = smu.get_traces()

voltage = np.array(data['voltage'])
current = np.array(data['current'])

plt.plot(voltage, current, linewidth=3, color='tomato')
plt.grid(color='green')

plt.show()