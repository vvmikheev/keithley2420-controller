from SMU_device import SMUDevice
from PUND.PUND_waveform import create_waveform
from PUND.plot_fig import *


instrument_id = 'GPIB0::24::INSTR'
smu = SMUDevice(instrument_id)
smu.connect()

"""
params is a dictionary with key parameters for a PUND sweep.

Vf - first voltage
Vs - second voltage
rise - number of measurements during the rise
hold - number of measurements to be done while maintaining the applied voltage
space - number of measurements between pulses
n_cycles - number of PUND cycles

Time required for a single measurement is approximately 1 ms. It is the limit for this SMU. The only way to control
rise/hold/space time is to change the number of measurements.
"""
params = {
            'Vf': -3,
            'Vs': 3,
            'rise': 20,
            'hold': 10,
            'space': 10,
            'n_cycles': 2,
        }
area = 200 ** 2 * 1e-8  # contact area in cm^2

waveform = []
for _ in range(params['n_cycles']):
    waveform = waveform + create_waveform(params)  # function "create_waveform() creates voltage list for given params"


smu.setup_sense_subsystem(compl=1e-5, rang=1e-5, nplc=0.1)
smu.custom_list_sweep(waveform, delay=0)

smu.enable_output()
smu.measure()
smu.wait()
smu.disable_output()

smu.check_for_errors()
data = smu.get_traces()
plot_fig(data, params, area, save=False)

