import os
import time
from pymodbus.client import ModbusTcpClient

LOG_FILE = "events.log"

client = ModbusTcpClient("127.0.0.1", port=5020)

if not client.connect():
    print("Could not connect to simulated PLC")
    exit()

try:
    while True:
        result = client.read_holding_registers(0, 6, slave=1)

        os.system("cls" if os.name == "nt" else "clear")

        print("========================================================")
        print(" OT LAB - INVESTIGATOR VIEW")
        print("========================================================")
        print()
        print(" EVENT TIMELINE")
        print("--------------------------------------------------------")

        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r", encoding="utf-8") as log_file:
                events = log_file.readlines()

            if events:
                for event in events[-10:]:
                    parts = event.strip().split("|", 2)

                    if len(parts) == 3:
                        timestamp, event_type, message = parts

                        print(
                            f" {timestamp} | "
                            f"{event_type:<10} | {message}"
                        )
            else:
                print(" No events recorded.")
        else:
            print(" No event log found.")

        print()
        print("--------------------------------------------------------")
        print(" CURRENT PROCESS STATE")
        print("--------------------------------------------------------")

        if result.isError():
            print(" Unable to read PLC state.")
        else:
            registers = result.registers

            setpoint = registers[0]
            actual = registers[1]
            valve = registers[2]
            pump = registers[3]
            flow = registers[4]
            alarm = registers[5]

            print(f" Setpoint            : {setpoint} C")
            print(f" Actual Temperature  : {actual} C")
            print(f" Valve Position      : {valve} %")
            print(f" Pump State          : {'ON' if pump == 1 else 'OFF'}")
            print(f" Flow Rate           : {flow} %")
            print(
                f" Alarm               : "
                f"{'LOW TEMPERATURE' if alarm == 1 else 'NORMAL'}"
            )

        print()
        print("--------------------------------------------------------")
        print(" INVESTIGATOR QUESTION")
        print("--------------------------------------------------------")
        print(" What happened before the process alarm?")
        print()
        print(" Press Ctrl+C to stop.")

        time.sleep(2)

except KeyboardInterrupt:
    print("\nInvestigator view stopped.")

finally:
    client.close()