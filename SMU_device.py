import pyvisa


class SMUDevice:

    def __init__(self, instruments_name):
        self.device = None
        self.instr_name = instruments_name

    def connect(self):
        """
        Connect to the device and make some preset. It has to be called after the class creation!
        """
        rm = pyvisa.ResourceManager()
        try:
            self.device = rm.open_resource(self.instr_name)
        except pyvisa.errors.VisaIOError:
            print(f'Device {self.instr_name} is not present in the system, check the connections.')

        self.device.write('*IDN?', 0)
        device_info = self.device.read()
        print(f'Device \n{device_info}is connected!')

        self.device.write(':SYST:BEEP:STAT OFF')
        self.disable_output()
        self.device.write('TRAC:CLE')
        self.device.timeout = None

    def check_for_errors(self):
        """
        Check if some errors occurred during the measurements. Raise warning in that case.
        Errors might appear in reversed order.
        """
        self.device.write('SYST:ERR:COUN?', 0)
        n_errors = int(self.device.read())
        if n_errors != 0:
            errors = []
            for i in range(n_errors):
                self.device.write('SYST:ERR:NEXT?', 0)
                errors.append(self.device.read())
            errors = ''.join(errors)
            raise Warning(f'An error occurred during measurements:\n {errors}')

    def wait(self):
        """
        Waiting for the device to finish.
        """
        self.device.write('*OPC?', 0)
        while True:
            try:
                self.device.read()
                break
            except pyvisa.errors.VisaIOError:
                continue

    def disable_display(self):
        self.device.write(':DISP:ENAB ON', 0)

    def enable_display(self):
        self.device.write(':DISP:ENAB OFF', 0)

    def setup_sense_subsystem(self, autorange=False, rang=1e-3, compl=None, nplc=0.01):
        """
        set up current sense subsystem
        :param autorange: bool (if enable autorange)
        :param rang: float (current range)
        :param compl: float (current compliance)
        :param nplc: float (min 0.01 nplc value)
        """
        self.device.write('SENS:FUNC:CONC OFF')
        self.device.write('SENS:FUNC:ON "CURR"')
        if compl is not None:
            self.device.write(f'SENS:CURR:PROT {compl}')
        if autorange:
            self.device.write('SENS:CURR:RANG:AUTO 1')
        else:
            self.device.write('SENS:CURR:RANG:AUTO 0')
            self.device.write(f'SENS:CURR:RANG {rang}')
        self.device.write(f'SENS:CURR:NPLC {max(0.01, nplc)}')

    def staircase_sweep(self, v_from, v_to, n_steps, delay=0.1):
        """
        set up staircase sweep (DC IV)
        :param v_from: float (start value)
        :param v_to: float (start value)
        :param n_steps: int (number of steps)
        :param delay: float (delay between a voltage increase and a measurement)
        """
        self.device.write('SOUR:FUNC VOLT')
        self.device.write(f':SOUR:VOLT:STAR {v_from}')
        self.device.write(f'SOUR:VOLT:STOP {v_to}')
        self.device.write(':SOUR:VOLT:MODE SWE')
        self.device.write(f'SOUR:SWE:POIN {n_steps}')
        self.device.write(f'SOUR:SWE:RANG BEST')

        self.device.write(f'TRIG:COUN {n_steps}')
        self.device.write(f'SOUR:DEL {delay}')

    def custom_list_sweep(self, waveform, delay=0):
        """
        setup custom waveform. Minimal distance between steps (with zero delay and nplc==0.01) is ~1 ms
        :param waveform: list (list of voltage values)
        :param delay: float (delay between voltage increase and measurements)
        """
        waveforms = []

        def splitter(list_to_split, splitted_lists):
            splitted_lists.append(list_to_split[:min(100, len(list_to_split))])
            list_to_split = list_to_split[100:]
            if list_to_split:
                return splitter(list_to_split, splitted_lists)
            else:
                return splitted_lists

        waveforms = splitter(waveform, waveforms)
        waveform_string = map(str, waveforms[0])
        waveform_string = ', '.join(waveform_string)
        self.device.write('SOUR:FUNC VOLT')
        self.device.write(':SOUR:VOLT:MODE LIST')
        self.device.write(f':SOUR:LIST:VOLT {waveform_string}')

        for splitted_waveform in waveforms[1:]:
            waveform_string = map(str, splitted_waveform)
            waveform_string = ', '.join(waveform_string)
            self.device.write(f':SOUR:LIST:VOLT:APP {waveform_string}')

        self.device.write('SOUR:VOLT:RANG:AUTO 0')
        self.device.write('SOUR:SWE:RANG FIX')
        self.device.write('SOUR:VOLT:RANG 10')
        self.device.write('SOUR:VOLT:PROT 10')
        self.device.write('SOUR:DEL:AUTO OFF')
        self.device.write(f'SOUR:DEL {delay}')
        self.device.write(':SYST:AZER OFF')
        self.device.write(f':TRIG:COUN {len(waveform)}')
        self.device.write('SOUR:DEL 0')

    def measure(self):
        """
        Starts the measure. Make sure to call turn on the output by calling .enable_output()
        """
        self.device.write('SYST:TIME:RES')
        self.device.write('INIT')

    def enable_output(self):
        """
        Turns on the output
        """
        self.device.write('OUTP ON')

    def disable_output(self):
        """
        Turns of the output. Make sure to call .wait() function before.
        """
        self.device.write('OUTP OFF')

    def get_traces(self):
        """
        Gather the data (time, voltage, current). Make sure to call .wait() function before!
        :return: dictionary, keys: 'time', 'voltage', 'current
        """
        self.device.write('FORM:ELEM TIME, VOLT, CURR')
        self.device.write('FETC?')
        result = self.device.read()
        result = result.split(',')
        result = list(map(float, result))
        data = {
            'time': result[2::3],
            'voltage': result[::3],
            'current': result[1::3]
        }
        return data

