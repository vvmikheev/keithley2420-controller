import numpy as np
import matplotlib.pyplot as plt

# params:
# Vf - first voltage
# Vs - second voltage
# dt - integration time
# rise - rise time
# hold- wait time
# space - space between pulses


def create_waveform(params):
    """
    Creates waveform for given parameters of a PUND sweep
    :param params: dict (params of a PUND sweep)
    :return: list of voltages to be send to SMU
    """

    params.update({'dt': 1})
    waveform = []
    space =[0] * (int(np.ceil(params['space'] / 2 / params['dt'])))
    for voltage in [params['Vf'], params['Vf'], params['Vs'], params['Vs']]:
        pulse = create_pulse(params, voltage)
        waveform = waveform + space + pulse + space
    return waveform


def create_pulse(params, voltage):
    raw_timescale = [0, params['rise'], params['hold'], params['rise']]
    raw_timescale = np.cumsum(raw_timescale)
    raw_voltage_series = [0, voltage, voltage, 0]
    true_scale = np.arange(0, raw_timescale[-1] + params['dt'], params['dt'])
    voltage_series = np.interp(true_scale, raw_timescale, raw_voltage_series, 0, 0)
    return voltage_series.tolist()


if __name__ == '__main__':
    params = {
        'Vf': 2.5,
        'Vs': -2.5,
        'dt': 1e-5,
        'rise': 1e-3,
        'hold': 1e-3,
        'space': 1e-3
    }
    v = np.array(create_waveform(params))
    t = np.arange(0, len(v) * params['dt'], params['dt'])
    plt.plot(t, v)
    plt.show()