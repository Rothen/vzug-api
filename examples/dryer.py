import asyncio
from vzug import Dryer
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

    device = Dryer(HOSTNAME_OR_IP, USERNAME, PASSWORD)
    await device.load_device_information()
    await device.load_program_details()
    await device.load_consumption_data()

    print("\n==== Device information")
    print("Type:", device.device_type)
    print("Model:", device.model_desc)
    print("Name:", device.device_name)
    print("Status:", device.status)
    print("Active:", device.is_active)

    print("\n==== Current Program")
    if device.is_active:
        print("Program name:", device.program_name)
        print("Program status:", device.program_status)
        print("End time:", device.date_time_end)
        print("Seconds to end:", device.seconds_to_end)
    else:
        print("No program active")

    print("\n==== Power Consumption")

    power_total = locale.format_string('%.0f', device.power_consumption_kwh_total, True)
    print(f"Power consumption total: {power_total} kWh, avg: {device.power_consumption_kwh_avg:.1f} kWh")

if __name__ == '__main__':
    asyncio.run(main())
