import asyncio

from vzug import Oven
import logconf
import locale
import sys

locale.setlocale(locale.LC_ALL, '')  # Use '' for auto, or force e.g. to 'en_US.UTF-8'

# First parameter must be the device IP address
HOSTNAME_OR_IP = sys.argv[1]
USERNAME = ""
PASSWORD = ""


async def main():
    logconf.setup_logging()

    device = Oven(HOSTNAME_OR_IP, USERNAME, PASSWORD)
    await device.load_device_information()
    await device.load_program_details()
    # await device.load_consumption_data()

    print("\n==== Device information")
    print("Type:", device.device_type)
    print("Model:", device.model_desc)
    print("Name:", device.device_name)
    print("Status:", device.status)
    print("Active:", device.is_active)

    print("\n==== Current Program")
    if device.is_active:
        print("ID:", device.program_id)
        print("Zone:", device.program_zone)
        print("Program Name:", device.program_name)
        print("Temp:", device.program_temp)
        print("Set Temp:", device.program_set_temp)
        print("Light:", device.program_light)
        print("Light Options:", device.program_light_options)
        print("Preheat Set:", device.program_preheat_set)
        print("Preheat Act:", device.program_preheat_act)
        print("Start Clearance:", device.program_start_clearance)
        print("Door Status:", device.program_door_status)
        print("Door Closed:", device.is_door_closed)
        print("Door Open:", device.is_door_open)
        print("Preheat Status:", device.preheat_status)
        print("Is Preheating:", device.is_preheating)
    else:
        print("No program active")

    '''print("\n==== Power Consumption")

    power_total = locale.format_string('%.0f', device.power_consumption_kwh_total, True)
    print(f"Power consumption total: {power_total} kWh, avg: {device.power_consumption_kwh_avg:.1f} kWh")'''

if __name__ == '__main__':
    asyncio.run(main())