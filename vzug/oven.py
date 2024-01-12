'''/ai?command=getModelDescription
/hh?command=getZHMode
/ai?command=getDeviceStatus
/ai?command=getLastPUSHNotifications
/hh?command=doTurnOff
/hh?command=setDeviceName'''

import locale

from datetime import datetime, timedelta
from .basic_device import BasicDevice, DeviceError, read_kwh_from_string
from .const import ENDPOINT_HH, COMMAND_GET_PROGRAM

locale.setlocale(locale.LC_ALL, '')  # Use '' for auto, or force e.g. to 'en_US.UTF-8'

PROGRAM_ID = 'id'
PROGRAM_STATUS = 'status'
PROGRAM_STATUS_VALUES_IDLE = 'idle'
PROGRAM_STATUS_VALUES_TIMED = 'timed'
PROGRAM_ZONE = 'zone'
PROGRAM_NAME = 'name'
PROGRAM_TEMP = 'temp'
PROGRAM_TEMP_SET = 'light'
PROGRAM_TEMP_ACT = 'act'
PROGRAM_LIGHT = 'light'
PROGRAM_LIGHT_SET = 'set'
PROGRAM_LIGHT_OPTIONS = 'options'
PROGRAM_PREHEAT = 'preheat'
PROGRAM_PREHEAT_SET = 'set'
PROGRAM_PREHEAT_ACT = 'act'
PROGRAM_START_CLEARANCE = 'startClearance'
PROGRAM_START_CLEARANCE_SET = 'set'
PROGRAM_DOOR_STATUS = 'doorStatus'
PROGRAM_DOOR_STATUS_ACT = 'act'
PROGRAM_PREHEAT_STATUS = 'preheatStatus'
PROGRAM_PREHEAT_STATUS_ACT = 'act'

REGEX_MATCH_LITER = r"(\d+(?:[\,\.]\d+)?).?ℓ"
REGEX_MATCH_KWH = r"(\d+(?:[\,\.]\d+)?).?kWh"


class Oven(BasicDevice):
    """Class representing V-Zug oven"""

    def __init__(self, host: str, username: str = "", password: str = ""):
        super().__init__(host, username, password)
        self._program_id = ""
        self._program_status = ""
        self._program_zone = ""
        self._program_name = ""
        self._program_temp = 0
        self._program_set_temp = 0
        self._program_light = False
        self._program_light_options = []
        self._program_preheat_set = False
        self._program_preheat_act = False
        self._program_start_clearance = False
        self._program_door_status = ""
        self._program_is_door_closed = False
        self._program_is_door_open = False
        self._program_preheat_status = ""
        self._program_is_heating = False
        self._power_consumption_kwh_total = 0.0
        self._power_consumption_kwh_avg = 0.0

    def _reset_active_program_information(self) -> None:
        self._program_id = ""
        self._program_status = ""
        self._program_zone = ""
        self._program_name = ""
        self._program_temp = 0
        self._program_set_temp = 0
        self._program_light = False
        self._program_light_options = []
        self._program_preheat_set = False
        self._program_preheat_act = False
        self._program_start_clearance = False
        self._program_door_status = ""
        self._program_is_door_closed = False
        self._program_is_door_open = False
        self._program_preheat_status = ""
        self._program_is_heating = False
        
    async def load_all_information(self) -> bool:
        """Load consumption data and if a program is active load also the program details"""
        loaded = await super().load_all_information()
        if loaded:
            
            if loaded and self.is_active:
                loaded = await self.load_program_details()
            
        return loaded

    async def load_program_details(self) -> bool:
        """Load program details information by calling the corresponding API endpoint"""

        self._logger.info("Loading program information for %s", self._host)

        self._reset_active_program_information()

        try:
            program_json = (await self.make_vzug_device_call_json(
                self.get_command_url(ENDPOINT_HH, COMMAND_GET_PROGRAM)))[0]

            self._program_status = program_json[PROGRAM_STATUS]
            
            if PROGRAM_STATUS_VALUES_IDLE in self._program_status:
                self._logger.info("No program information available because no program is active")
                return False

            '''if PROGRAM_STATUS_VALUES_TIMED in self._program_status:
                self._program_duration = program_json[PROGRAM_DURATION][PROGRAM_DURATION_SET]
                self._seconds_to_start = program_json[PROGRAM_STARTTIME][PROGRAM_STARTTIME_SET]
                self._seconds_to_end = self._seconds_to_start + self._program_duration
            else:
                self._seconds_to_end = program_json[PROGRAM_DURATION][PROGRAM_DURATION_ACT]'''

            self._program_id = program_json[PROGRAM_ID]
            self._program_zone = program_json[PROGRAM_ZONE]
            self._program_name = program_json[PROGRAM_NAME]
            self._program_temp = program_json[PROGRAM_TEMP][PROGRAM_TEMP_ACT]
            self._program_set_temp = program_json[PROGRAM_TEMP][PROGRAM_TEMP_SET]
            self._program_light = program_json[PROGRAM_LIGHT][PROGRAM_LIGHT_SET]
            self._program_light_options = program_json[PROGRAM_LIGHT][PROGRAM_LIGHT_OPTIONS]
            self._program_preheat_set = program_json[PROGRAM_PREHEAT][PROGRAM_PREHEAT_SET]
            self._program_preheat_act = program_json[PROGRAM_PREHEAT][PROGRAM_PREHEAT_ACT]
            self._program_start_clearance = program_json[PROGRAM_START_CLEARANCE][PROGRAM_START_CLEARANCE_SET]
            self._program_door_status = program_json[PROGRAM_DOOR_STATUS][PROGRAM_DOOR_STATUS_ACT]
            self._program_is_door_closed = self._program_door_status == 'closed'
            self._program_is_door_open = not self._program_is_door_closed
            self._program_preheat_status = program_json[PROGRAM_PREHEAT_STATUS][PROGRAM_PREHEAT_STATUS_ACT]
            self._program_is_heating = self._program_preheat_status == 'heating'

            self._logger.info("Go program information. Active program: %s, minutes to end: %.0f, end time: %s",
                              self.program_name, self.seconds_to_end / 60, self.date_time_end)

            return True

        except DeviceError as e:
            self._error_code = e.error_code
            self._error_message = e.message
            self._error_exception = e
            return False

    '''async def load_consumption_data(self) -> bool:
        """Load power consumption data by calling the corresponding API endpoint"""

        self._logger.info("Loading power consumption data for %s", self._host)
        try:
            consumption_total = await self.do_consumption_details_request(CMD_VALUE_CONSUMP_DRYER_TOTAL)
            self._power_consumption_kwh_total = read_kwh_from_string(consumption_total)

            consumption_avg = await self.do_consumption_details_request(CMD_VALUE_CONSUMP_DRYER_AVG)
            self._power_consumption_kwh_avg = read_kwh_from_string(consumption_avg)
            
            self._logger.info("Power consumption total: %s kWh, avg: %.1f kWh",
                              locale.format_string('%.0f', self._power_consumption_kwh_total, True),
                              self._power_consumption_kwh_avg)

        except DeviceError as e:
            self._error_code = e.error_code
            self._error_message = e.message
            self._error_exception = e
            return False

        return True'''

    @property
    def program_id(self) -> int:
        return self._program_id

    @property
    def program_status(self) -> str:
        return self._program_status

    @property
    def program_zone(self) -> str:
        return self._program_zone

    @property
    def program_name(self) -> str:
        return self._program_name

    @property
    def program_temp(self) -> int:
        return self._program_temp

    @property
    def program_set_temp(self) -> int:
        return self._program_set_temp

    @property
    def program_light(self) -> bool:
        return self._program_light

    @property
    def program_light_options(self) -> list:
        return self._program_light_options

    @property
    def program_preheat_set(self) -> bool:
        return self._program_preheat_set

    @property
    def program_preheat_act(self) -> bool:
        return self._program_preheat_act

    @property
    def program_start_clearance(self) -> bool:
        return self._program_start_clearance

    @property
    def program_door_status(self) -> str:
        return self._program_door_status

    @property
    def is_door_closed(self) -> bool:
        return self._program_is_door_closed

    @property
    def is_door_open(self) -> bool:
        return self._program_is_door_open

    @property
    def preheat_status(self) -> str:
        return self._program_preheat_status

    @property
    def is_preheating(self) -> bool:
        return self._program_is_heating
