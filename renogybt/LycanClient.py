import logging

from .BaseClient import BaseClient
from .Utils import bytes_to_int, parse_temperature

# Read and parse BT-1 RS232 type bluetooth module connected to Renogy Lycan
# Does not support Communication Hub with multiple devices connected

FUNCTION = {
    3: "READ",
    6: "WRITE"
}

CHARGING_STATE = {
    0: 'deactivated',
    1: 'activated',
    2: 'mppt',
    3: 'equalizing',
    4: 'boost',
    5: 'floating',
    6: 'current limiting'
}

LOAD_STATE = {
  0: 'off',
  1: 'on'
}

BATTERY_TYPE = {
    1: 'open',
    2: 'sealed',
    3: 'gel',
    4: 'lithium',
    5: 'custom'
}

class LycanClient(BaseClient):
    def __init__(self, config, on_data_callback=None):
        super().__init__(config)
        self.on_data_callback = on_data_callback
        self.data = {}
        self.sections = [
            {'register': 4000, 'words': 8, 'parser': self.parse_inverter_stats},
            {'register': 4311, 'words': 8, 'parser': self.parse_inverter_model},
            {'register': 4329, 'words': 5, 'parser': self.parse_solar_charging},
            {'register': 4410, 'words': 2, 'parser': self.parse_inverter_load},
            # {'register': 0x20c, 'words': 22, 'parser': self.parse_more_info},
            # {'register': 0x107, 'words': 1, 'parser': self.parse_voltage_info},
            # {'register': 26, 'words': 1, 'parser': self.parse_device_address}
            {'register': 0x100, 'words': 16, 'parser': self.parse_chargin_info},
            {'register': 57348, 'words': 1, 'parser': self.parse_battery_type}
        ]
        self.set_load_params = {'function': 6, 'register': 266}

    def on_data_received(self, response):
        operation = bytes_to_int(response, 1, 1)
        if operation == 6: # write operation
            self.parse_set_load_response(response)
            self.on_write_operation_complete()
            self.data = {}
        else:
            # read is handled in base class
            super().on_data_received(response)

    def on_write_operation_complete(self):
        logging.info("on_write_operation_complete")
        if self.on_data_callback is not None:
            self.on_data_callback(self, self.data)

    def set_load(self, value = 0):
        logging.info("setting load {}".format(value))
        request = self.create_generic_read_request(self.device_id, self.set_load_params["function"], self.set_load_params["register"], value)
        self.device.characteristic_write_value(request)

    def parse_voltage_info(self, bs):
        logging.info("parse_voltage_info")
        data = {}
        data['voltage'] = bytes_to_int(bs, 3, 2)
        self.data.update(data)

    def parse_device_address(self, bs):
        logging.info("parse_device_address")
        data = {}
        data['device_id'] = bytes_to_int(bs, 4, 1)
        self.data.update(data)

    def parse_chargin_info(self, bs):
        data = {}
        temp_unit = self.config['data']['temperature_unit']
        data['function'] = FUNCTION.get(bytes_to_int(bs, 1, 1))
        data['battery_percentage'] = bytes_to_int(bs, 3, 2)
        data['battery_voltage'] = bytes_to_int(bs, 5, 2, scale = 0.1)
        raw_value = bytes_to_int(bs, 7, 2)
        raw_value = (raw_value - 65536) if raw_value > 32768 else raw_value
        data['battery_current'] = raw_value * 0.01
        # data['battery_temperature'] = parse_temperature(bytes_to_int(bs, 10, 1), temp_unit)
        # data['controller_temperature'] = parse_temperature(bytes_to_int(bs, 9, 1), temp_unit)
        # data['load_status'] = LOAD_STATE.get(bytes_to_int(bs, 67, 1) >> 7)
        # data['load_voltage'] = bytes_to_int(bs, 11, 2, scale = 0.1)
        # data['load_current'] = bytes_to_int(bs, 13, 2, scale = 0.01)
        # data['load_power'] = bytes_to_int(bs, 15, 2)
        data['pv_voltage'] = bytes_to_int(bs, 17, 2, scale = 0.1) 
        data['pv_current'] = bytes_to_int(bs, 19, 2, scale = 0.1)
        data['pv_power'] = bytes_to_int(bs, 21, 2)
        # data['max_charging_power_today'] = bytes_to_int(bs, 33, 2)
        # data['max_discharging_power_today'] = bytes_to_int(bs, 35, 2)
        # data['charging_amp_hours_today'] = bytes_to_int(bs, 37, 2)
        # data['discharging_amp_hours_today'] = bytes_to_int(bs, 39, 2)
        # data['power_generation_today'] = bytes_to_int(bs, 41, 2)
        # data['power_consumption_today'] = bytes_to_int(bs, 43, 2)
        # data['power_generation_total'] = bytes_to_int(bs, 59, 4)
        # data['charging_status'] = CHARGING_STATE.get(bytes_to_int(bs, 68, 1))
        self.data.update(data)

    def parse_more_info(self, bs):
        logging.info("parse_more_info")
        data = {}
        data['more1'] = bytes_to_int(bs, 3, 2)
        data['more2'] = bytes_to_int(bs, 5, 2)
        data['more3'] = bytes_to_int(bs, 7, 2)
        data['more4'] = bytes_to_int(bs, 9, 2)
        data['more5'] = bytes_to_int(bs, 11, 2)
        data['more6'] = bytes_to_int(bs, 13, 2)
        data['more7'] = bytes_to_int(bs, 15, 2)
        data['more8'] = bytes_to_int(bs, 17, 2)
        data['more9'] = bytes_to_int(bs, 19, 2)
        data['more10'] = bytes_to_int(bs, 21, 2)
        data['more11'] = bytes_to_int(bs, 23, 2)
        data['more12'] = bytes_to_int(bs, 25, 2)
        data['more13'] = bytes_to_int(bs, 27, 2)
        data['more14'] = bytes_to_int(bs, 29, 2)
        data['more15'] = bytes_to_int(bs, 31, 2)
        data['more16'] = bytes_to_int(bs, 33, 2)
        data['more17'] = bytes_to_int(bs, 35, 2)
        data['more18'] = bytes_to_int(bs, 37, 2)
        self.data.update(data)

    def parse_battery_type(self, bs):
        data = {}
        data['function'] = FUNCTION.get(bytes_to_int(bs, 1, 1))
        data['battery_type'] = BATTERY_TYPE.get(bytes_to_int(bs, 3, 2))
        self.data.update(data)


    def parse_inverter_stats(self, bs):
        logging.info(f"parse_inverter_stats {bs.hex()}")
        data = {}
        data['function'] = FUNCTION.get(bytes_to_int(bs, 1, 1))
        data['uei_voltage'] = bytes_to_int(bs, 3, 2, scale=0.1)
        data['uei_current'] = bytes_to_int(bs, 5, 2, scale=0.1)
        data['voltage'] = bytes_to_int(bs, 7, 2, scale=0.1)
        data['load_current'] = bytes_to_int(bs, 9, 2)
        data['frequency'] = bytes_to_int(bs, 11, 2, scale=0.01)
        data['temperature'] = bytes_to_int(bs, 13, 2, scale=0.1)
        self.data.update(data)

    def parse_inverter_model(self, bs):
        logging.info(f"parse_inverter_model {bs.hex()}")
        data = {}
        data['model'] = (bs[3:15]).decode('utf-8')
        self.data.update(data)

    def parse_solar_charging(self, bs):
        logging.info(f"parse_solar_charging {bs.hex()}")
        data = {}
        data['solar_voltage'] = bytes_to_int(bs, 3, 2, scale=0.1)
        data['solar_current'] = bytes_to_int(bs, 5, 2, scale=0.1)
        data['solar_power'] = bytes_to_int(bs, 7, 2)
        data['solar_charging_state'] = CHARGING_STATE.get(bytes_to_int(bs, 9, 2))
        data['solar_charging_power'] = bytes_to_int(bs, 11, 2)
        self.data.update(data)

    def parse_inverter_load(self, bs):
        logging.info(f"parse_inverter_load {bs.hex()}")
        data = {}
        data['load_power'] = bytes_to_int(bs, 3, 2)
        data['charging_current'] = bytes_to_int(bs, 5, 2, scale=0.1)
        self.data.update(data)

    def parse_battery_type(self, bs):
        data = {}
        data['function'] = FUNCTION.get(bytes_to_int(bs, 1, 1))
        data['battery_type'] = BATTERY_TYPE.get(bytes_to_int(bs, 3, 2))
        self.data.update(data)

    def parse_set_load_response(self, bs):
        data = {}
        data['function'] = FUNCTION.get(bytes_to_int(bs, 1, 1))
        data['load_status'] = bytes_to_int(bs, 5, 1)
        self.data.update(data)
